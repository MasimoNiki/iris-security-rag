# IRIS publishing checklist

This checklist separates what is already ready from what should be completed before a public `v1.0.0` release.

## Ready now

- [x] English and Russian README files.
- [x] English and Russian engineering case studies.
- [x] Editable DOCX and shareable PDF reports.
- [x] Architecture, query-flow, retrieval-quality, and retrieval-latency visuals.
- [x] Grafana screenshots from the operational batch run.
- [x] Raw retrieval and batch artifacts stored in `data/eval/`.
- [x] `.env.example` without secrets.
- [x] Third-party source notices.
- [x] Technical notes moved under `docs/technical/`.

## High priority before public release

1. **Choose the project code license.** Add `LICENSE` only after deciding whether the intended model is MIT, Apache-2.0, or another license.
2. **Complete corpus provenance.** The latest audit flags eight manually added or legacy documents with missing fields such as `external_id`, `source_url`, and `source_revision`.
3. **Replace the NIST-aligned summary.** Use a revision-pinned current official NIST publication or clearly keep the summary outside the official-source corpus.
4. **Calibrate the no-answer guard.** Fix the `q004` false rejection and rerun answerable/unanswerable validation.
5. **Capture one real GUI screenshot.** Use a successful cited answer and hide browser chrome if possible. Save it as `docs/images/gui-answer.png`, then replace the representative answer visual in the README if the screenshot is stronger.
6. **Rerun all checks.** Record the actual `pytest`, `ruff check .`, and `ruff format --check .` results in the release notes.
7. **Verify a clean clone.** Follow README Quick Start on a new directory or machine.

## Recommended GitHub polish

- Add a concise repository description and topics: `rag`, `llm`, `fastapi`, `qdrant`, `postgresql`, `ollama`, `prometheus`, `grafana`, `cybersecurity`.
- Pin the repository on the GitHub profile.
- Add GitHub Actions for tests and Ruff, then add CI badges only after the workflow passes.
- Use the architecture image or query example as the social preview.
- Create a `v1.0.0` release with the PDF report and a concise change summary.
- Link the repository and case study from the CV/portfolio with one result-focused sentence.

Suggested CV line:

> Built a local-first SOC RAG system with hybrid retrieval, multilingual reranking, cited Ollama answers, evaluation, and Prometheus/Grafana observability; achieved 100% Content Hit@5 and 0.972 Content MRR on a 50-question retrieval benchmark.

## Final release evidence

Keep these artifacts together for reproducibility:

```text
data/eval/golden_questions.yml
data/eval/retrieval_comparison.json
data/eval/query_batch_results.json
data/audit/latest_corpus_audit.json
data/manifests/corpus_sources.json
docs/images/grafana-overview.png
docs/images/grafana-latency.png
docs/reports/IRIS_CASE_STUDY_EN.pdf
docs/reports/IRIS_CASE_STUDY_RU.pdf
```
