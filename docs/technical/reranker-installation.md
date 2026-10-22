# Установка optional reranker

Распакуйте архив в корень проекта:

```text
D:\IRIS_soc\IRIS_soc
```

с сохранением структуры папок и заменой файлов. Не заменяйте свой `.env`
файлом `.env.example`.

Новые зависимости не нужны: `CrossEncoder` входит в уже установленный
`sentence-transformers`.

Добавьте в существующий `.env`:

```dotenv
RERANKER_ENABLED=false
RERANKER_MODEL_NAME=cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
RERANKER_CANDIDATE_POOL_SIZE=20
RERANKER_BATCH_SIZE=4
RERANKER_MAX_LENGTH=512
RERANKER_FAIL_OPEN=true
```

`RERANKER_ENABLED=false` оставляет текущий hybrid-поиск основным. Скрипт
сравнения всё равно явно проверит профиль с reranker, поэтому сначала не нужно
включать его для всех API-запросов.

## Проверка кода

```cmd
ruff format app tests scripts\run_eval.py scripts\compare_retrieval.py
ruff check app tests scripts\run_eval.py scripts\compare_retrieval.py
pytest
```

Миграции Alembic, повторный ingestion и переиндексация Qdrant не нужны.

## Сравнение трёх профилей

```cmd
python scripts\compare_retrieval.py
```

Скрипт последовательно проверит:

1. `dense`;
2. `hybrid`;
3. `hybrid_reranked`.

Перед измерением каждого профиля выполняется один прогревочный запрос. При
первом запуске профиль `hybrid_reranked` автоматически скачает модель с
Hugging Face. Предупреждение об отсутствии `HF_TOKEN` не является ошибкой.

Подробный отчёт будет сохранён в:

```text
data/eval/retrieval_comparison.json
```

В выводе для `hybrid_reranked` должно быть:

```text
Reranker applied: 100% of questions
```

Если указано меньше 100%, reranker не применился ко всем запросам и сравнивать
его метрики с hybrid как полноценный эксперимент нельзя.

## Ручная проверка API

После перезапуска FastAPI:

```cmd
uvicorn app.main:app --reload
```

в `POST /api/v1/search` можно сравнить один запрос без reranker:

```json
{
  "query": "Какие признаки могут указывать на ransomware?",
  "top_k": 5,
  "strategy": "hybrid",
  "rerank": false
}
```

и с reranker:

```json
{
  "query": "Какие признаки могут указывать на ransomware?",
  "top_k": 5,
  "strategy": "hybrid",
  "rerank": true
}
```

В reranked-ответе появятся поля `pre_rerank_rank`, `reranker_rank`,
`reranker_score` и `reranker_latency_ms`. Поле `score` останется исходным
cosine score и продолжит использоваться защитным порогом генерации.

Включайте reranker по умолчанию только после сравнения:

```dotenv
RERANKER_ENABLED=true
```

Если модель не загрузится, `RERANKER_FAIL_OPEN=true` сохранит исходный порядок
hybrid и API продолжит работу. В таком ответе `reranker_applied` будет `false`.
