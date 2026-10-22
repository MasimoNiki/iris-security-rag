from fastapi import APIRouter

from app.core.config import settings
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.retrieval.retriever import get_retriever

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search_chunks(request: SearchRequest) -> SearchResponse:
    strategy = request.strategy or settings.retrieval_strategy
    reranker_enabled = (
        request.rerank if request.rerank is not None else settings.reranker_enabled
    )
    retriever = get_retriever(
        strategy,
        reranker_enabled=reranker_enabled,
    )

    retrieved_chunks = retriever.search(
        query=request.query,
        top_k=request.top_k,
    )

    results = [
        SearchResult(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            title=chunk.title,
            content=chunk.content,
            score=chunk.score,
            source_type=chunk.source_type,
            local_path=chunk.local_path,
            language=chunk.language,
            section_title=chunk.section_title,
            metadata=chunk.metadata,
            retrieval_strategy=chunk.retrieval_strategy,
            dense_score=chunk.dense_score,
            lexical_score=chunk.lexical_score,
            fusion_score=chunk.fusion_score,
            dense_rank=chunk.dense_rank,
            lexical_rank=chunk.lexical_rank,
            reranker_score=chunk.reranker_score,
            pre_rerank_rank=chunk.pre_rerank_rank,
            reranker_rank=chunk.reranker_rank,
            reranker_latency_ms=chunk.reranker_latency_ms,
        )
        for chunk in retrieved_chunks
    ]
    reranker_applied = any(result.reranker_score is not None for result in results)

    return SearchResponse(
        query=request.query,
        top_k=request.top_k,
        strategy=strategy,
        reranker_enabled=reranker_enabled,
        reranker_applied=reranker_applied,
        reranker_model=settings.reranker_model_name if reranker_enabled else None,
        results=results,
    )
