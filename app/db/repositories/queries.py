from sqlalchemy.orm import Session

from app.db.models import Query


def create_query(
    db: Session,
    *,
    question: str,
    answer: str | None = None,
    language: str | None = None,
    retrieval_strategy: str | None = None,
    llm_provider: str | None = None,
    latency_ms: int | None = None,
) -> Query:
    query = Query(
        question=question,
        answer=answer,
        language=language,
        retrieval_strategy=retrieval_strategy,
        llm_provider=llm_provider,
        latency_ms=latency_ms,
    )

    db.add(query)
    db.commit()
    db.refresh(query)

    return query
