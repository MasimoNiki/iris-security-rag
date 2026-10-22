from __future__ import annotations

from app.services.retrieval.retriever import (
    BM25Index,
    HybridRetriever,
    RerankingRetriever,
    RetrievedChunk,
    tokenize_for_bm25,
)


def make_chunk(
    chunk_id: int,
    content: str,
    *,
    score: float = 0.0,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=chunk_id,
        chunk_index=0,
        title=f"Document {chunk_id}",
        content=content,
        score=score,
        source_type="test",
        local_path=f"data/{chunk_id}.md",
        language="en",
        section_title="Description",
        metadata={},
        dense_score=score if score else None,
    )


class StubRetriever:
    def __init__(self, results: list[RetrievedChunk]) -> None:
        self.results = results

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        return self.results[:top_k]


class StubReranker:
    model_name = "test-reranker"

    def __init__(self, scores_by_chunk_id: dict[int, float]) -> None:
        self.scores_by_chunk_id = scores_by_chunk_id

    def score(
        self,
        query: str,
        chunks: list[RetrievedChunk],
    ) -> list[float]:
        return [self.scores_by_chunk_id[chunk.chunk_id] for chunk in chunks]


class FailingReranker:
    model_name = "failing-reranker"

    def score(
        self,
        query: str,
        chunks: list[RetrievedChunk],
    ) -> list[float]:
        raise RuntimeError("Model unavailable")


def test_bm25_tokenizer_preserves_security_identifiers() -> None:
    tokens = tokenize_for_bm25(
        "CVE-2031-9999 and findstr.exe inspect LSASS.",
    )

    assert "cve-2031-9999" in tokens
    assert "cve" in tokens
    assert "2031" in tokens
    assert "findstr.exe" in tokens
    assert "findstr" in tokens
    assert "lsass" in tokens


def test_bm25_index_ranks_exact_identifier_match_first() -> None:
    index = BM25Index(
        [
            make_chunk(1, "General credential access guidance."),
            make_chunk(2, "T1003 OS Credential Dumping targets LSASS memory."),
            make_chunk(3, "Ransomware response and containment."),
        ]
    )

    results = index.search("What does T1003 do to LSASS?", top_k=3)

    assert results[0].chunk_id == 2
    assert results[0].lexical_score
    assert results[0].lexical_rank == 1


def test_bm25_document_frequency_counts_documents_not_term_repetitions() -> None:
    index = BM25Index(
        [
            make_chunk(1, "LSASS LSASS LSASS LSASS"),
            make_chunk(2, "A different process"),
        ]
    )

    results = index.search("LSASS", top_k=2)

    assert results[0].chunk_id == 1
    assert results[0].lexical_score is not None
    assert results[0].lexical_score > 0.0


def test_hybrid_rrf_promotes_chunk_found_by_both_channels() -> None:
    dense_results = [
        make_chunk(1, "Semantic result", score=0.80),
        make_chunk(2, "Shared result", score=0.70),
    ]
    lexical_results = [
        make_chunk(2, "Shared result"),
        make_chunk(3, "Exact-only result"),
    ]
    lexical_results[0].lexical_score = 4.0
    lexical_results[1].lexical_score = 3.0

    retriever = HybridRetriever(
        dense_retriever=StubRetriever(dense_results),
        lexical_retriever=StubRetriever(lexical_results),
        dense_weight=0.6,
        lexical_weight=0.4,
        rrf_k=60,
        candidate_pool_size=3,
    )

    results = retriever.search("test query", top_k=3)

    assert results[0].chunk_id == 2
    assert results[0].dense_score == 0.70
    assert results[0].lexical_score == 4.0
    assert results[0].fusion_score is not None
    assert results[0].retrieval_strategy == "hybrid"


def test_hybrid_keeps_dense_score_for_generation_guard() -> None:
    dense_result = make_chunk(1, "Dense result", score=0.63)
    lexical_result = make_chunk(1, "Dense result")
    lexical_result.lexical_score = 2.0

    retriever = HybridRetriever(
        dense_retriever=StubRetriever([dense_result]),
        lexical_retriever=StubRetriever([lexical_result]),
        candidate_pool_size=1,
    )

    result = retriever.search("test", top_k=1)[0]

    assert result.score == 0.63
    assert result.dense_score == 0.63


def test_reranker_changes_order_and_preserves_retrieval_scores() -> None:
    candidates = [
        make_chunk(1, "Weak passage", score=0.80),
        make_chunk(2, "Relevant passage", score=0.65),
        make_chunk(3, "Other passage", score=0.60),
    ]
    candidates[0].fusion_score = 0.95
    candidates[1].fusion_score = 0.80

    retriever = RerankingRetriever(
        base_retriever=StubRetriever(candidates),
        reranker=StubReranker({1: -2.0, 2: 4.0, 3: 0.5}),
        candidate_pool_size=3,
    )

    results = retriever.search("Which passage is relevant?", top_k=2)

    assert [result.chunk_id for result in results] == [2, 3]
    assert results[0].score == 0.65
    assert results[0].fusion_score == 0.80
    assert results[0].pre_rerank_rank == 2
    assert results[0].reranker_rank == 1
    assert results[0].reranker_score == 4.0
    assert results[0].reranker_latency_ms is not None


def test_reranker_fail_open_keeps_original_order() -> None:
    candidates = [
        make_chunk(1, "First", score=0.80),
        make_chunk(2, "Second", score=0.70),
    ]
    retriever = RerankingRetriever(
        base_retriever=StubRetriever(candidates),
        reranker=FailingReranker(),
        candidate_pool_size=2,
        fail_open=True,
    )

    results = retriever.search("test", top_k=2)

    assert [result.chunk_id for result in results] == [1, 2]
    assert all(result.reranker_score is None for result in results)
    assert [result.pre_rerank_rank for result in results] == [1, 2]
