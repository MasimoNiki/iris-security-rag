from __future__ import annotations

import math
import re
import time
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from functools import lru_cache
from logging import getLogger
from typing import TYPE_CHECKING, Any, Literal, Protocol

if TYPE_CHECKING:
    from app.services.embeddings.provider import SentenceTransformerEmbeddingProvider
    from app.services.vector_store.qdrant import QdrantVectorStore

from app.core.config import settings

RetrievalStrategy = Literal["dense", "hybrid"]
logger = getLogger(__name__)


@dataclass
class RetrievedChunk:
    chunk_id: int
    document_id: int
    chunk_index: int | None
    title: str | None
    content: str
    score: float
    source_type: str | None
    local_path: str | None
    language: str | None
    section_title: str | None
    metadata: dict[str, Any]
    retrieval_strategy: RetrievalStrategy = "dense"
    dense_score: float | None = None
    lexical_score: float | None = None
    fusion_score: float | None = None
    dense_rank: int | None = None
    lexical_rank: int | None = None
    reranker_score: float | None = None
    pre_rerank_rank: int | None = None
    reranker_rank: int | None = None
    reranker_latency_ms: float | None = None


class Retriever(Protocol):
    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]: ...


class Reranker(Protocol):
    @property
    def model_name(self) -> str: ...

    def score(
        self,
        query: str,
        chunks: Sequence[RetrievedChunk],
    ) -> list[float]: ...


def _retrieved_chunk_from_payload(
    *,
    point_id: int,
    payload: dict[str, Any],
    score: float,
) -> RetrievedChunk | None:
    chunk_id = payload.get("chunk_id") or point_id
    document_id = payload.get("document_id")

    if document_id is None:
        return None

    return RetrievedChunk(
        chunk_id=int(chunk_id),
        document_id=int(document_id),
        chunk_index=payload.get("chunk_index"),
        title=payload.get("document_title"),
        content=payload.get("content", ""),
        score=score,
        source_type=payload.get("source_type"),
        local_path=payload.get("local_path"),
        language=payload.get("language"),
        section_title=payload.get("section_title"),
        metadata=payload.get("chunk_metadata") or {},
        retrieval_strategy="dense",
        dense_score=score,
    )


class DenseRetriever:
    def __init__(
        self,
        embedding_provider: SentenceTransformerEmbeddingProvider | None = None,
        vector_store: QdrantVectorStore | None = None,
    ) -> None:
        if embedding_provider is None:
            from app.services.embeddings.provider import (
                SentenceTransformerEmbeddingProvider,
            )

            embedding_provider = SentenceTransformerEmbeddingProvider()

        if vector_store is None:
            from app.services.vector_store.qdrant import QdrantVectorStore

            vector_store = QdrantVectorStore()

        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        query_vector = self.embedding_provider.embed_query(query)

        points = self.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
        )

        results: list[RetrievedChunk] = []

        for rank, point in enumerate(points, start=1):
            payload = point.payload or {}
            chunk = _retrieved_chunk_from_payload(
                point_id=int(point.id),
                payload=payload,
                score=float(point.score),
            )
            if chunk is None:
                continue

            chunk.dense_rank = rank
            results.append(chunk)

        return results


TOKEN_PATTERN = re.compile(
    r"[^\W_]+(?:[._:/\\-][^\W_]+)*",
    flags=re.UNICODE,
)
TOKEN_SEPARATOR_PATTERN = re.compile(r"[._:/\\-]+")


def tokenize_for_bm25(text: str) -> list[str]:
    """Tokenize prose and preserve security identifiers such as T1003 or LSASS."""
    tokens: list[str] = []

    for match in TOKEN_PATTERN.finditer(text.casefold()):
        token = match.group(0)
        tokens.append(token)

        parts = [
            part
            for part in TOKEN_SEPARATOR_PATTERN.split(token)
            if len(part) > 1 and part != token
        ]
        tokens.extend(parts)

    return tokens


def _build_lexical_text(chunk: RetrievedChunk) -> str:
    metadata = chunk.metadata or {}
    metadata_parts: list[str] = []

    for key in ("external_id", "source_url", "tags", "domain"):
        value = metadata.get(key)
        if isinstance(value, list):
            metadata_parts.extend(str(item) for item in value)
        elif value is not None:
            metadata_parts.append(str(value))

    return "\n".join(
        part
        for part in (
            chunk.title,
            chunk.section_title,
            chunk.content,
            chunk.source_type,
            chunk.local_path,
            *metadata_parts,
        )
        if part
    )


class BM25Index:
    def __init__(
        self,
        chunks: Iterable[RetrievedChunk],
        *,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self.chunks = list(chunks)
        self.k1 = k1
        self.b = b
        self.term_frequencies: list[Counter[str]] = []
        self.document_lengths: list[int] = []
        document_frequencies: Counter[str] = Counter()

        for chunk in self.chunks:
            tokens = tokenize_for_bm25(_build_lexical_text(chunk))
            frequencies = Counter(tokens)
            self.term_frequencies.append(frequencies)
            self.document_lengths.append(len(tokens))
            document_frequencies.update(frequencies.keys())

        self.average_document_length = (
            sum(self.document_lengths) / len(self.document_lengths)
            if self.document_lengths
            else 0.0
        )
        document_count = len(self.chunks)
        self.inverse_document_frequencies = {
            term: math.log(1.0 + (document_count - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequencies.items()
        }

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        if not self.chunks or top_k < 1:
            return []

        query_terms = set(tokenize_for_bm25(query))
        scored: list[tuple[float, int]] = []

        for index, frequencies in enumerate(self.term_frequencies):
            score = self._score_document(
                query_terms=query_terms,
                frequencies=frequencies,
                document_length=self.document_lengths[index],
            )
            if score > 0.0:
                scored.append((score, index))

        scored.sort(
            key=lambda item: (-item[0], self.chunks[item[1]].chunk_id),
        )

        results: list[RetrievedChunk] = []
        for rank, (score, index) in enumerate(scored[:top_k], start=1):
            source = self.chunks[index]
            results.append(
                RetrievedChunk(
                    chunk_id=source.chunk_id,
                    document_id=source.document_id,
                    chunk_index=source.chunk_index,
                    title=source.title,
                    content=source.content,
                    score=0.0,
                    source_type=source.source_type,
                    local_path=source.local_path,
                    language=source.language,
                    section_title=source.section_title,
                    metadata=source.metadata,
                    retrieval_strategy="hybrid",
                    lexical_score=score,
                    lexical_rank=rank,
                )
            )

        return results

    def _score_document(
        self,
        *,
        query_terms: set[str],
        frequencies: Counter[str],
        document_length: int,
    ) -> float:
        if not query_terms or self.average_document_length <= 0.0:
            return 0.0

        length_normalization = (
            1.0 - self.b + (self.b * document_length / self.average_document_length)
        )
        score = 0.0

        for term in query_terms:
            term_frequency = frequencies.get(term, 0)
            if term_frequency == 0:
                continue

            inverse_document_frequency = self.inverse_document_frequencies.get(
                term,
                0.0,
            )
            numerator = term_frequency * (self.k1 + 1.0)
            denominator = term_frequency + self.k1 * length_normalization
            score += inverse_document_frequency * numerator / denominator

        return score


def _load_chunks_from_postgres() -> list[RetrievedChunk]:
    from sqlalchemy.orm import joinedload

    from app.db.models import Chunk
    from app.db.session import SessionLocal

    with SessionLocal() as db:
        chunks = (
            db.query(Chunk).options(joinedload(Chunk.document)).order_by(Chunk.id).all()
        )

        results: list[RetrievedChunk] = []
        for chunk in chunks:
            document = chunk.document
            metadata = dict(chunk.metadata_json or {})

            if document:
                metadata.update(
                    {
                        "external_id": document.external_id,
                        "source_url": document.source_url,
                        "tags": (document.metadata_json or {}).get("tags", []),
                        "domain": document.domain,
                    }
                )

            results.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    title=document.title if document else None,
                    content=chunk.content,
                    score=0.0,
                    source_type=document.source_type if document else None,
                    local_path=document.local_path if document else None,
                    language=document.language if document else None,
                    section_title=chunk.section_title,
                    metadata=metadata,
                    retrieval_strategy="hybrid",
                )
            )

        return results


class LexicalRetriever:
    def __init__(
        self,
        chunks_loader: Callable[[], list[RetrievedChunk]] | None = None,
        *,
        k1: float | None = None,
        b: float | None = None,
    ) -> None:
        self._chunks_loader = chunks_loader or _load_chunks_from_postgres
        self._k1 = k1 if k1 is not None else settings.bm25_k1
        self._b = b if b is not None else settings.bm25_b
        self._index: BM25Index | None = None

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        if self._index is None:
            self._index = BM25Index(
                self._chunks_loader(),
                k1=self._k1,
                b=self._b,
            )

        return self._index.search(query=query, top_k=top_k)

    def reload(self) -> None:
        self._index = None


class HybridRetriever:
    def __init__(
        self,
        dense_retriever: Retriever | None = None,
        lexical_retriever: Retriever | None = None,
        *,
        dense_weight: float | None = None,
        lexical_weight: float | None = None,
        rrf_k: int | None = None,
        candidate_pool_size: int | None = None,
    ) -> None:
        self.dense_retriever = dense_retriever or DenseRetriever()
        self.lexical_retriever = lexical_retriever or LexicalRetriever()
        self.dense_weight = (
            dense_weight if dense_weight is not None else settings.hybrid_dense_weight
        )
        self.lexical_weight = (
            lexical_weight
            if lexical_weight is not None
            else settings.hybrid_lexical_weight
        )
        self.rrf_k = rrf_k if rrf_k is not None else settings.hybrid_rrf_k
        self.candidate_pool_size = (
            candidate_pool_size
            if candidate_pool_size is not None
            else settings.hybrid_candidate_pool_size
        )

        if self.dense_weight + self.lexical_weight <= 0.0:
            raise ValueError("At least one hybrid retrieval weight must be positive.")

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        candidate_limit = max(top_k, self.candidate_pool_size)
        dense_results = self.dense_retriever.search(query, top_k=candidate_limit)
        lexical_results = self.lexical_retriever.search(query, top_k=candidate_limit)

        chunks: dict[int, RetrievedChunk] = {}
        fusion_scores: defaultdict[int, float] = defaultdict(float)

        for rank, chunk in enumerate(dense_results, start=1):
            chunks[chunk.chunk_id] = chunk
            chunk.retrieval_strategy = "hybrid"
            chunk.dense_score = (
                chunk.dense_score if chunk.dense_score is not None else chunk.score
            )
            chunk.dense_rank = rank
            fusion_scores[chunk.chunk_id] += self.dense_weight / (self.rrf_k + rank)

        for rank, lexical_chunk in enumerate(lexical_results, start=1):
            chunk = chunks.get(lexical_chunk.chunk_id)
            if chunk is None:
                chunk = lexical_chunk
                chunks[chunk.chunk_id] = chunk

            chunk.retrieval_strategy = "hybrid"
            chunk.lexical_score = lexical_chunk.lexical_score
            chunk.lexical_rank = rank
            fusion_scores[chunk.chunk_id] += self.lexical_weight / (self.rrf_k + rank)

        ideal_score = (self.dense_weight + self.lexical_weight) / (self.rrf_k + 1)

        for chunk_id, fusion_score in fusion_scores.items():
            chunks[chunk_id].fusion_score = (
                fusion_score / ideal_score if ideal_score > 0.0 else 0.0
            )

        ranked = sorted(
            chunks.values(),
            key=lambda chunk: (
                -(chunk.fusion_score or 0.0),
                -(chunk.dense_score or 0.0),
                chunk.chunk_id,
            ),
        )

        return ranked[:top_k]


def _build_reranker_text(chunk: RetrievedChunk) -> str:
    return "\n".join(
        part
        for part in (
            chunk.title,
            chunk.section_title,
            chunk.content,
        )
        if part
    )


class CrossEncoderReranker:
    def __init__(
        self,
        *,
        model_name: str | None = None,
        batch_size: int | None = None,
        max_length: int | None = None,
    ) -> None:
        self._model_name = model_name or settings.reranker_model_name
        self.batch_size = batch_size or settings.reranker_batch_size
        self.max_length = max_length or settings.reranker_max_length
        self._model: Any | None = None

    @property
    def model_name(self) -> str:
        return self._model_name

    def _load_model(self) -> Any:
        if self._model is None:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(
                self.model_name,
                device="cpu",
                max_length=self.max_length,
            )

        return self._model

    def score(
        self,
        query: str,
        chunks: Sequence[RetrievedChunk],
    ) -> list[float]:
        if not chunks:
            return []

        pairs = [(query, _build_reranker_text(chunk)) for chunk in chunks]
        predictions = self._load_model().predict(
            pairs,
            batch_size=self.batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        values = (
            predictions.tolist()
            if hasattr(predictions, "tolist")
            else list(predictions)
        )
        if not isinstance(values, list):
            values = [values]

        scores: list[float] = []
        for value in values:
            if isinstance(value, list):
                if len(value) != 1:
                    raise ValueError("Reranker must return one score per candidate.")
                value = value[0]
            scores.append(float(value))

        return scores


class RerankingRetriever:
    def __init__(
        self,
        base_retriever: Retriever,
        reranker: Reranker | None = None,
        *,
        candidate_pool_size: int | None = None,
        fail_open: bool | None = None,
    ) -> None:
        self.base_retriever = base_retriever
        self.reranker = reranker or CrossEncoderReranker()
        self.candidate_pool_size = (
            candidate_pool_size
            if candidate_pool_size is not None
            else settings.reranker_candidate_pool_size
        )
        self.fail_open = (
            fail_open if fail_open is not None else settings.reranker_fail_open
        )

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        candidate_limit = max(top_k, self.candidate_pool_size)
        candidates = self.base_retriever.search(query, top_k=candidate_limit)

        for rank, chunk in enumerate(candidates, start=1):
            chunk.pre_rerank_rank = rank

        if not candidates:
            return []

        started_at = time.perf_counter()
        try:
            scores = self.reranker.score(query, candidates)
            if len(scores) != len(candidates):
                raise ValueError(
                    "Reranker returned a different number of scores than candidates."
                )
        except Exception:
            if not self.fail_open:
                raise

            logger.exception(
                "Reranker failed; returning the original retrieval order.",
            )
            return candidates[:top_k]

        latency_ms = (time.perf_counter() - started_at) * 1000
        scored = list(zip(candidates, scores, strict=True))
        scored.sort(
            key=lambda item: (
                -item[1],
                item[0].pre_rerank_rank or 0,
                item[0].chunk_id,
            ),
        )

        ranked: list[RetrievedChunk] = []
        for rank, (chunk, score) in enumerate(scored, start=1):
            chunk.reranker_score = score
            chunk.reranker_rank = rank
            chunk.reranker_latency_ms = latency_ms
            ranked.append(chunk)

        return ranked[:top_k]


def normalize_retrieval_strategy(strategy: str | None) -> RetrievalStrategy:
    value = (strategy or settings.retrieval_strategy).strip().lower()
    if value not in {"dense", "hybrid"}:
        raise ValueError(
            f"Unsupported retrieval strategy: {value}. Use 'dense' or 'hybrid'."
        )

    return value


@lru_cache
def _get_retriever(
    strategy: RetrievalStrategy,
    reranker_enabled: bool,
) -> Retriever:
    if strategy == "dense":
        retriever: Retriever = DenseRetriever()
    else:
        retriever = HybridRetriever()

    if reranker_enabled:
        return RerankingRetriever(retriever)

    return retriever


def get_retriever(
    strategy: str | None = None,
    *,
    reranker_enabled: bool | None = None,
) -> Retriever:
    should_rerank = (
        settings.reranker_enabled if reranker_enabled is None else reranker_enabled
    )
    return _get_retriever(
        normalize_retrieval_strategy(strategy),
        should_rerank,
    )
