# IRIS: hybrid search

Hybrid retrieval combines:

- semantic dense retrieval from Qdrant;
- lexical BM25 retrieval over PostgreSQL chunks;
- weighted Reciprocal Rank Fusion (RRF).

The lexical index is built lazily on the first hybrid request and remains in
memory. Restart the FastAPI process after ingestion so it is rebuilt from the
latest PostgreSQL chunks. No database migration or Qdrant reindex is required.

## Configuration

Add these values to `.env`:

```dotenv
RETRIEVAL_STRATEGY=hybrid
HYBRID_DENSE_WEIGHT=0.60
HYBRID_LEXICAL_WEIGHT=0.40
HYBRID_RRF_K=60
HYBRID_CANDIDATE_POOL_SIZE=50
BM25_K1=1.5
BM25_B=0.75
```

`dense` remains available as a reproducible baseline:

```dotenv
RETRIEVAL_STRATEGY=dense
```

Both `/api/v1/search` and `/api/v1/query` accept an optional per-request
override:

```json
{
  "query": "What is OS Credential Dumping used for?",
  "top_k": 5,
  "strategy": "hybrid"
}
```

Hybrid search results expose:

- `score`: original dense cosine score used by the generation safety guard;
- `dense_score` and `dense_rank`;
- `lexical_score` and `lexical_rank`;
- `fusion_score`: normalized weighted RRF score used for final ordering.

Do not compare `fusion_score` with the dense `RAG_MIN_RETRIEVAL_SCORE`; these
values have different meanings and scales.

## Retrieval-only evaluation

This command evaluates both strategies without calling Ollama:

```cmd
python scripts\compare_retrieval.py
```

The detailed report is saved to:

```text
data/eval/retrieval_comparison.json
```

The main metrics to compare with `baseline_dense_v2` are:

- Document Hit@5;
- Content Hit@5;
- Document MRR;
- Content MRR;
- average retrieval latency.

For the full RAG evaluation with generation, choose the strategy explicitly:

```cmd
python scripts\run_eval.py --retrieval-strategy hybrid
```

On a CPU-only laptop this command also calls Ollama for every question and can
take a long time. Use `compare_retrieval.py` first when measuring search quality.
