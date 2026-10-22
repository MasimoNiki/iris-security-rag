# IRIS Security RAG

[English](README.md) | [Русский](README_RU.md)

Локальная RAG-система для SOC-аналитиков. IRIS ищет информацию в курируемом корпусе по информационной безопасности, объединяет семантический и лексический поиск, при необходимости переранжирует документы и формирует ответы с цитатами через локальную модель Ollama.

![Пример ответа IRIS](docs/images/query-example.png)

## Результаты в цифрах

- **108 документов / 994 чанка** из MITRE ATT&CK, Sigma, OWASP, NIST-ориентированного обзора и runbook-инструкций.
- **100% Content Hit@5** и **0,972 Content MRR** для hybrid search с reranker на 50 answerable-вопросах.
- **20/20 успешных HTTP-запросов** в массовом прогоне: 19 ответов, 1 контролируемый `no-answer`, 0 fallback.
- **100% сгенерированных ответов содержали источники** в batch-эксперименте.

> Answer rate 95% не является accuracy. Качество retrieval измеряется отдельно на golden dataset, а массовый прогон проверяет полный HTTP-путь и наблюдаемость системы.

## Зачем нужен проект

SOC-аналитику приходится быстро сопоставлять runbook-инструкции, техники ATT&CK, Sigma-правила и рекомендации по безопасности приложений. IRIS исследует практическую инженерную задачу: как небольшая CPU-friendly RAG-система может извлекать проверяемый контекст, отклонять слабые результаты, цитировать источники и показывать собственные метрики.

## Основные возможности

- Ingestion Markdown, TXT и YAML с отдельным parser для Sigma.
- Воспроизводимая загрузка корпуса с фиксацией upstream-ревизий и SHA-256 manifest.
- Метаданные документов, чанки и история запросов в PostgreSQL.
- Мультиязычный dense search в Qdrant.
- Lexical retrieval, взвешенный Reciprocal Rank Fusion и опциональный cross-encoder reranker.
- Ollama и OpenAI-compatible providers с extractive fallback.
- Ответы с цитатами, confidence metadata и retrieval-based no-answer guard.
- REST API на FastAPI и адаптивный веб-интерфейс.
- Golden dataset, HTTP batch-runner, Prometheus metrics и Grafana dashboard.
- Проверки Pytest и Ruff.

Redis поднят в Docker Compose как задел для будущего кеширования, но пока не используется в query pipeline.

## Архитектура

![Архитектура IRIS](docs/images/architecture.png)

В online-пути dense и lexical кандидаты объединяются с помощью weighted RRF. Опциональный reranker переставляет расширенный набор кандидатов, после чего лучшие контексты передаются генератору. PostgreSQL хранит метаданные, чанки, полнотекстовые данные и историю запросов; Qdrant хранит векторы и retrieval payload.

## Корпус

| Источник | Документов | Чанков | Происхождение |
|---|---:|---:|---|
| MITRE ATT&CK | 30 | 277 | Официальные STIX-данные, преобразованные в Markdown |
| Sigma | 64 | 461 | Официальные правила SigmaHQ, преобразованные из YAML |
| OWASP Top 10:2025 | 10 | 214 | Официальные Markdown-документы OWASP |
| NIST-ориентированный обзор ransomware | 1 | 10 | Самостоятельно составленный обзор, не официальный документ NIST |
| SOC runbooks | 3 | 32 | Синтетические русскоязычные инструкции |
| **Всего** | **108** | **994** | |

Manifest официальных источников фиксирует репозиторий и commit для 100 загруженных документов. Текущий corpus audit также отмечает восемь добавленных вручную или legacy-документов с неполными provenance-полями; это отражено в ограничениях.

## Оценка retrieval

Для всех конфигураций использованы одинаковые 50 answerable-вопросов, `top_k=5` и один корпус.

| Конфигурация | Document Hit@5 | Content Hit@5 | Keyword Recall@5 | Content MRR | Средняя latency |
|---|---:|---:|---:|---:|---:|
| Dense | 98% | 94% | 86,0% | 0,844 | 68 мс |
| Hybrid | 100% | 98% | 90,3% | 0,913 | 79 мс |
| Hybrid + reranker | 100% | 100% | 93,7% | 0,972 | 1 287 мс |

![Сравнение качества retrieval](docs/images/retrieval-quality.png)

Hybrid search даёт лучший баланс скорости и качества. Reranker достигает максимального результата на content-level, но добавляет около 1,2 секунды. При этом primary/document MRR немного ниже, чем у hybrid без reranker, хотя Content MRR существенно выше — в проекте показаны обе стороны компромисса.

Исходные результаты: [`data/eval/retrieval_comparison.json`](data/eval/retrieval_comparison.json).

## Массовый operational-прогон

6 августа 2026 года один warm-up и 20 измеряемых запросов `hybrid + reranker` были последовательно отправлены в `/api/v1/query` на ноутбуке с Windows 10, 16 ГБ RAM и CPU-only inference.

| Метрика | Результат |
|---|---:|
| Успешные HTTP-запросы | 20 / 20 |
| Сгенерированные ответы | 19 |
| Контролируемые no-answer | 1 |
| Ответы с источниками | 100% |
| Fallback | 0 |
| Средняя end-to-end latency | 63,45 с |
| p50 / p95 latency | 70,68 с / 83,44 с |
| Средняя latency reranker | 1,18 с |
| Полное время | 24 мин 55 с |

Grafana показывает 21 запрос, потому что учитывает warm-up.

![Обзор batch-прогона в Grafana](docs/images/grafana-overview.png)

Главный bottleneck — локальная генерация, а не retrieval. Это ожидаемый результат для `qwen3:4b` на CPU, поэтому он описан как ограничение эксперимента, а не как production latency.

Исходные результаты: [`data/eval/query_batch_results.json`](data/eval/query_batch_results.json).

## Пример API

```http
POST /api/v1/query
Content-Type: application/json

{
  "query": "Как Sigma может обнаружить запуск Empire PowerShell?",
  "top_k": 5,
  "strategy": "hybrid",
  "rerank": true
}
```

Ответ содержит `answer`, `is_answerable`, `confidence`, процитированные `sources`, а также metadata по latency и provider. После запуска Swagger доступен по адресу `http://127.0.0.1:8000/docs`.

## Быстрый запуск на Windows

Нужны Python 3.11+, Docker Desktop и [Ollama](https://ollama.com/).

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
docker compose up -d
alembic upgrade head
ollama pull qwen3:4b
```

Подготовь официальный корпус, выполни ingestion и перестрой индекс:

```cmd
python scripts\fetch_corpus_sources.py --sigma-count 60
python scripts\ingest_local_docs.py
python scripts\index_qdrant.py --recreate
```

Укажи `LLM_PROVIDER=ollama` в `.env`, затем запусти приложение:

```cmd
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Web UI: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/api/v1/health`
- Prometheus metrics: `http://127.0.0.1:8000/metrics`
- Grafana: `http://127.0.0.1:3000`

Проверки:

```cmd
pytest
ruff check .
ruff format --check .
```

Воспроизводимый массовый эксперимент:

```cmd
python scripts\run_query_batch.py --limit 20 --strategy hybrid --reranker
```

## Структура проекта

```text
app/                 FastAPI, retrieval, generation, ingestion, observability
data/                корпус, manifest, audit и evaluation-артефакты
docs/                case study, изображения, отчёты и technical notes
infra/               конфигурация Prometheus и Grafana
migrations/          Alembic migrations
scripts/             corpus, indexing, evaluation, audit и batch utilities
tests/               тесты API и сервисов
```

## Ограничения

- Генерация измерялась на CPU; latency нельзя переносить на GPU или облачный inference.
- Golden dataset содержит 55 вопросов: 50 answerable и 5 unanswerable.
- Batch-отчёт не оценивает фактическую правильность текста ответа.
- No-answer guard опирается на retrieval score и отклонил `q004`, несмотря на сильный reranker score; нужна калибровка threshold.
- Corpus audit отмечает неполные provenance-поля у восьми добавленных вручную или legacy-документов.
- NIST-ориентированный обзор и три runbook являются самостоятельными материалами, а не официальными документами.
- Redis пока не подключён к query pipeline.
- IRIS — прототип системы поддержки решений, а не автономный инструмент реагирования; аналитик должен проверять источники.

## Дальнейшее развитие

- Откалибровать no-answer guard на answerable и unanswerable validation-наборах.
- Дополнить provenance metadata и заменить NIST summary на официальный источник с зафиксированной ревизией.
- Реализовать cache policy и подключить Redis.
- Добавить оценку качества генерации с human или model-assisted rubric.
- Добавить CI, контейнеризовать API и сравнить GPU/hosted inference.

## Документация

- [Case study на английском](docs/IRIS_CASE_STUDY_EN.md)
- [Case study на русском](docs/IRIS_CASE_STUDY_RU.md)
- [PDF-отчёт на английском](docs/reports/IRIS_CASE_STUDY_EN.pdf)
- [PDF-отчёт на русском](docs/reports/IRIS_CASE_STUDY_RU.pdf)
- [Checklist перед публикацией](docs/PUBLISHING_CHECKLIST.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)

## Attribution и статус лицензии

Открытые материалы по информационной безопасности остаются под условиями своих источников; подробности указаны в [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Лицензия для собственного кода проекта пока намеренно не выбрана. Перед публичным релизом `v1.0.0` её необходимо определить и добавить.
