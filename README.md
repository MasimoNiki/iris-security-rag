# IRIS Security RAG

[English](README.md) | [Русский](README_RU.md)

Local-first retrieval-augmented generation system for SOC analysts. IRIS searches a curated security corpus, combines dense and lexical retrieval, optionally reranks evidence, and produces cited answers through a local Ollama model.

![Representative IRIS answer](docs/images/query-example.png)

## Results at a glance

- **108 documents / 994 chunks** across MITRE ATT&CK, Sigma, OWASP, a NIST-aligned summary, and incident-response runbooks.
- **100% Content Hit@5** and **0.972 Content MRR** with hybrid retrieval plus reranking on 50 answerable golden questions.
- **20/20 successful HTTP requests** in the operational batch run; 19 answers, 1 guarded no-answer, 0 fallbacks.
- **100% of generated answers included sources** in the batch experiment.

> The 95% batch answer rate is not an accuracy metric. Retrieval quality is evaluated separately on the golden dataset; the batch run validates the end-to-end HTTP path and observability.

## Why this project exists

SOC analysts often need to connect operational runbooks, ATT&CK techniques, Sigma detections, and application-security guidance under time pressure. IRIS explores a practical engineering question: how can a small, CPU-friendly RAG system retrieve defensible evidence, reject weak context, cite sources, and expose its own performance?

## Core capabilities

- Markdown, TXT, and YAML ingestion with a dedicated Sigma parser.
- Reproducible corpus fetcher with pinned upstream revisions and SHA-256 manifests.
- Chunk metadata and query history in PostgreSQL.
- Multilingual dense search in Qdrant.
- Lexical retrieval, weighted Reciprocal Rank Fusion, and optional cross-encoder reranking.
- Ollama and OpenAI-compatible generation providers with extractive fallback.
- Citation-aware answers, confidence metadata, and a retrieval-based no-answer guard.
- FastAPI REST API and a responsive web interface.
- Golden-dataset evaluation, batch HTTP runner, Prometheus metrics, and Grafana dashboards.
- Pytest and Ruff checks.

Redis is provisioned in Docker Compose for future caching; it is not used in the current query path.

## Architecture

![IRIS architecture](docs/images/architecture.png)

The online path joins vector and lexical candidates through weighted RRF. The optional reranker reorders a larger candidate pool before the top contexts are passed to the generator. PostgreSQL stores document metadata, chunks, full-text data, and query records; Qdrant stores vectors and retrieval payloads.

## Corpus

| Source | Documents | Chunks | Provenance |
|---|---:|---:|---|
| MITRE ATT&CK | 30 | 277 | Official STIX data, transformed to Markdown |
| Sigma | 64 | 461 | Official SigmaHQ rules, transformed from YAML |
| OWASP Top 10:2025 | 10 | 214 | Official OWASP Markdown |
| NIST-aligned ransomware summary | 1 | 10 | Manually curated summary; not an official NIST publication |
| SOC runbooks | 3 | 32 | Synthetic Russian-language runbooks |
| **Total** | **108** | **994** | |

The official-source manifest records the upstream repository and commit for 100 fetched documents. The current corpus audit also flags eight manually added or legacy documents that still need complete provenance fields; see [Limitations](#limitations).

## Retrieval evaluation

The comparison uses the same 50 answerable questions, `top_k=5`, and corpus for every configuration.

| Configuration | Document Hit@5 | Content Hit@5 | Keyword Recall@5 | Content MRR | Avg latency |
|---|---:|---:|---:|---:|---:|
| Dense | 98% | 94% | 86.0% | 0.844 | 68 ms |
| Hybrid | 100% | 98% | 90.3% | 0.913 | 79 ms |
| Hybrid + reranker | 100% | 100% | 93.7% | 0.972 | 1,287 ms |

![Retrieval quality comparison](docs/images/retrieval-quality.png)

Hybrid retrieval gives the strongest speed-quality trade-off. Reranking reaches the best content-level result but adds about 1.2 seconds on the test laptop. Its primary/document MRR is slightly lower than hybrid-only MRR, while content MRR improves substantially; the project reports both instead of hiding the trade-off.

Raw results: [`data/eval/retrieval_comparison.json`](data/eval/retrieval_comparison.json).

## Operational batch run

On 6 August 2026, one warm-up request and 20 measured `hybrid + reranker` requests were sent sequentially through `/api/v1/query` on a Windows 10, CPU-only laptop with 16 GB RAM.

| Metric | Result |
|---|---:|
| Successful HTTP requests | 20 / 20 |
| Generated answers | 19 |
| Guarded no-answers | 1 |
| Answers with sources | 100% |
| Fallbacks | 0 |
| Average end-to-end latency | 63.45 s |
| p50 / p95 latency | 70.68 s / 83.44 s |
| Average reranker latency | 1.18 s |
| Total wall time | 24 min 55 s |

Grafana shows 21 total queries because it includes the warm-up request.

![Grafana batch overview](docs/images/grafana-overview.png)

The dominant bottleneck is local generation, not retrieval. This is expected for `qwen3:4b` on CPU and is documented as an experimental constraint rather than presented as production latency.

Raw results: [`data/eval/query_batch_results.json`](data/eval/query_batch_results.json).

## API example

```http
POST /api/v1/query
Content-Type: application/json

{
  "query": "How can Sigma detect an Empire PowerShell launch?",
  "top_k": 5,
  "strategy": "hybrid",
  "rerank": true
}
```

The response contains `answer`, `is_answerable`, `confidence`, cited `sources`, and latency/provider metadata. Interactive API documentation is available at `http://127.0.0.1:8000/docs` after startup.

## Quick start on Windows

Requirements: Python 3.11+, Docker Desktop, and [Ollama](https://ollama.com/).

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
docker compose up -d
alembic upgrade head
ollama pull qwen3:4b
```

Prepare or refresh the official corpus, ingest it, and build the vector index:

```cmd
python scripts\fetch_corpus_sources.py --sigma-count 60
python scripts\ingest_local_docs.py
python scripts\index_qdrant.py --recreate
```

Set `LLM_PROVIDER=ollama` in `.env`, then start the application:

```cmd
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Web UI: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/v1/health`
- Prometheus metrics: `http://127.0.0.1:8000/metrics`
- Grafana: `http://127.0.0.1:3000`

Run checks:

```cmd
pytest
ruff check .
ruff format --check .
```

Run the reproducible operational experiment:

```cmd
python scripts\run_query_batch.py --limit 20 --strategy hybrid --reranker
```

## Project layout

```text
app/                 FastAPI, retrieval, generation, ingestion, observability
data/                corpus, manifests, audits, and evaluation artifacts
docs/                case studies, images, reports, and technical notes
infra/               Prometheus and Grafana provisioning
migrations/          Alembic migrations
scripts/             corpus, indexing, evaluation, audit, and batch utilities
tests/               API and service tests
```

## Limitations

- Local generation was measured on CPU; latency is not representative of GPU or hosted inference.
- The golden dataset contains 55 questions (50 answerable and 5 unanswerable) and remains modest.
- The operational batch report does not calculate answer correctness.
- The no-answer guard uses retrieval scores and rejected `q004` despite strong reranker evidence; threshold calibration is required.
- The corpus audit flags incomplete provenance metadata for eight manually added or legacy documents.
- The bundled NIST-aligned summary and three runbooks are manually authored, not official source documents.
- Redis is provisioned but not yet connected to the query path.
- IRIS is a decision-support prototype, not an autonomous incident-response system; analysts must verify evidence.

## Roadmap

- Calibrate the no-answer guard using answerable and unanswerable validation sets.
- Complete provenance metadata and replace the NIST summary with a revision-pinned official source.
- Add cache policy and connect Redis.
- Evaluate generation quality with human or model-assisted rubrics.
- Add CI, containerize the API, and benchmark GPU/hosted inference.

## Documentation

- [English case study](docs/IRIS_CASE_STUDY_EN.md)
- [Russian case study](docs/IRIS_CASE_STUDY_RU.md)
- [English PDF report](docs/reports/IRIS_CASE_STUDY_EN.pdf)
- [Russian PDF report](docs/reports/IRIS_CASE_STUDY_RU.pdf)
- [Publishing checklist](docs/PUBLISHING_CHECKLIST.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)

## Attribution and license status

Open-source security content remains subject to its upstream terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). A project code license has intentionally not been selected yet. Choose and add one before publishing a public `v1.0.0` release.
