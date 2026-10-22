# IRIS Optional Reranker

Reranking добавляет второй, более точный этап сортировки после быстрого поиска:

```text
question
  -> dense + BM25
  -> weighted RRF
  -> top 20 candidates
  -> multilingual CrossEncoder
  -> top 5 contexts
  -> LLM answer
```

Используется модель
`cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`. Она обучена на multilingual
MMARCO, поэтому подходит для смешанного русского и английского корпуса. Модель
работает локально и загружается лениво только при первом reranked-запросе.

Reranker получает пары `(question, chunk)` и оценивает их совместно. Это
медленнее bi-encoder retrieval, поэтому он применяется только к 20 кандидатам,
а не ко всему корпусу.

## Диагностические поля

- `pre_rerank_rank`: место после dense/BM25/RRF;
- `reranker_score`: score cross-encoder;
- `reranker_rank`: место после reranking;
- `reranker_latency_ms`: время reranker без первого этапа retrieval;
- `reranker_applied`: признак успешного применения модели.

Логит `reranker_score` нельзя сравнивать с cosine score и использовать вместо
`RAG_MIN_RETRIEVAL_SCORE`. Поэтому исходные `score`, `dense_score`,
`lexical_score` и `fusion_score` сохраняются без изменений.

## Отказоустойчивость

При `RERANKER_FAIL_OPEN=true` ошибка скачивания или inference не ломает `/search`
и `/query`: система возвращает исходный hybrid-порядок. Evaluation дополнительно
показывает долю запросов, для которых reranker действительно был применён.
