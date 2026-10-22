# Установка этапа Hybrid Search

Распакуйте архив в корень проекта:

```text
D:\IRIS_soc\IRIS_soc
```

с сохранением структуры папок и заменой файлов.

Добавьте в существующий `.env`:

```dotenv
RETRIEVAL_STRATEGY=hybrid
HYBRID_DENSE_WEIGHT=0.60
HYBRID_LEXICAL_WEIGHT=0.40
HYBRID_RRF_K=60
HYBRID_CANDIDATE_POOL_SIZE=50
BM25_K1=1.5
BM25_B=0.75
```

Не заменяйте свой `.env` файлом `.env.example`.

Проверьте код:

```cmd
ruff format app tests scripts\run_eval.py scripts\compare_retrieval.py
ruff check app tests scripts\run_eval.py scripts\compare_retrieval.py
pytest
```

Перезапустите FastAPI:

```cmd
uvicorn app.main:app --reload
```

Миграции Alembic, повторный ingestion и переиндексация Qdrant не нужны.

## Проверка через Swagger

В `POST /api/v1/search` можно явно сравнить стратегии:

```json
{
  "query": "Какие параметры PowerShell считаются подозрительными?",
  "top_k": 5,
  "strategy": "dense"
}
```

и:

```json
{
  "query": "Какие параметры PowerShell считаются подозрительными?",
  "top_k": 5,
  "strategy": "hybrid"
}
```

Для hybrid итоговый порядок определяется `fusion_score`. Поле `score`
сохраняет cosine score dense-поиска для совместимости с защитным порогом
генерации.

## Сравнение evaluation

Запустите retrieval-only сравнение:

```cmd
python scripts\compare_retrieval.py
```

Оно не обращается к Ollama и поэтому быстро отработает на CPU. Пришлите полный
вывод и файл:

```text
data/eval/retrieval_comparison.json
```

После оценки зафиксируйте лучший профиль отдельным полным RAG-прогоном:

```cmd
python scripts\run_eval.py --retrieval-strategy hybrid --baseline-output data\eval\baseline_hybrid_v1.json
```

Этот полный прогон вызывает текущий LLM-провайдер для всех вопросов и с
`qwen3:4b` на CPU может занять много времени.
