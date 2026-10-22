from pathlib import Path

import httpx

from app.services.evaluation.query_batch import (
    BatchQuestion,
    QueryBatchRunner,
    load_batch_questions,
    summarize_batch,
)


def test_load_batch_questions_accepts_golden_and_plain_items(tmp_path: Path) -> None:
    dataset = tmp_path / "questions.yml"
    dataset.write_text(
        """
- id: known
  question: Known question?
  answerable: true
- Plain question?
""".strip(),
        encoding="utf-8",
    )

    questions = load_batch_questions(dataset)

    assert questions == [
        BatchQuestion("known", "Known question?", True),
        BatchQuestion("q002", "Plain question?", None),
    ]


def test_query_batch_runner_parses_success_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/query"
        return httpx.Response(
            200,
            json={
                "answer": "Use MFA [1].",
                "is_answerable": True,
                "confidence": 0.82,
                "sources": [
                    {
                        "citation_id": 1,
                        "chunk_id": 10,
                        "document_id": 2,
                        "title": "Access Control",
                        "source_type": "owasp",
                        "score": 0.77,
                        "metadata": {"external_id": "A01"},
                        "reranker_score": 0.91,
                    }
                ],
                "metadata": {
                    "llm_provider": "ollama",
                    "retrieval_strategy": "hybrid",
                    "latency_ms": 1200,
                    "fallback_used": False,
                    "cited_source_ids": [1],
                    "reranker_enabled": True,
                    "reranker_applied": True,
                    "reranker_latency_ms": 120.0,
                },
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(
        base_url="http://testserver",
        transport=transport,
    ) as client:
        runner = QueryBatchRunner(
            client=client,
            endpoint="/api/v1/query",
            top_k=5,
            strategy="hybrid",
            reranker_enabled=True,
        )
        result = runner.run_question(
            question=BatchQuestion("q001", "What is access control?", True),
            sequence=1,
            iteration=1,
        )

    assert result.status == "success"
    assert result.provider == "ollama"
    assert result.sources_count == 1
    assert result.sources[0]["external_id"] == "A01"
    assert result.reranker_applied is True


def test_query_batch_runner_records_http_error() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(500, json={"detail": "failure"})
    )
    with httpx.Client(
        base_url="http://testserver",
        transport=transport,
    ) as client:
        runner = QueryBatchRunner(
            client=client,
            endpoint="/api/v1/query",
            top_k=5,
            strategy="dense",
            reranker_enabled=False,
        )
        result = runner.run_question(
            question=BatchQuestion("q001", "Question?"),
            sequence=1,
            iteration=1,
        )

    assert result.status == "error"
    assert result.http_status == 500
    assert result.error


def test_summarize_batch_calculates_dashboard_statistics() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "answer": "Answer [1].",
                "is_answerable": True,
                "confidence": 0.8,
                "sources": [{"citation_id": 1}],
                "metadata": {
                    "llm_provider": "ollama",
                    "retrieval_strategy": "hybrid",
                    "reranker_applied": True,
                    "fallback_used": False,
                },
            },
        )
    )
    with httpx.Client(
        base_url="http://testserver",
        transport=transport,
    ) as client:
        runner = QueryBatchRunner(
            client=client,
            endpoint="/api/v1/query",
            top_k=5,
            strategy="hybrid",
            reranker_enabled=True,
        )
        result = runner.run_question(
            question=BatchQuestion("q001", "Question?", True),
            sequence=1,
            iteration=1,
        )

    summary = summarize_batch(
        [result],
        planned_requests=1,
        interrupted=False,
    )

    assert summary["successful_requests"] == 1
    assert summary["answer_rate"] == 1.0
    assert summary["answers_with_sources_rate"] == 1.0
    assert summary["answerability_accuracy"] == 1.0
    assert summary["reranker_applied_count"] == 1

