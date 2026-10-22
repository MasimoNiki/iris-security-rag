from __future__ import annotations

import argparse
import time
from pathlib import Path

import httpx

from app.services.evaluation.query_batch import (
    QueryBatchRunner,
    load_batch_questions,
    save_batch_report,
    summarize_batch,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Send a sequential batch of questions through the IRIS /query API. "
            "This populates Prometheus/Grafana metrics."
        ),
    )
    parser.add_argument(
        "--dataset",
        default="data/eval/golden_questions.yml",
        help="YAML or JSON file containing questions.",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL of the running IRIS API.",
    )
    parser.add_argument(
        "--endpoint",
        default="/api/v1/query",
        help="Query endpoint path.",
    )
    parser.add_argument(
        "--health-endpoint",
        default="/api/v1/health",
        help="Health endpoint checked before the batch starts.",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--strategy",
        choices=("dense", "hybrid"),
        default="hybrid",
    )
    parser.add_argument(
        "--reranker",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable or disable the reranker (enabled by default).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Questions per iteration; use 0 for the entire dataset.",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of times to repeat the selected questions.",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=1,
        help="Warm-up requests excluded from the report but visible in metrics.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Delay in seconds between measured requests.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=300.0,
        help="Timeout for each request in seconds.",
    )
    parser.add_argument(
        "--output",
        default="data/eval/query_batch_results.json",
        help="Path for the JSON report.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop after the first failed request.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.top_k < 1 or args.top_k > 20:
        raise ValueError("--top-k must be between 1 and 20.")
    if args.limit < 0:
        raise ValueError("--limit must be 0 or greater.")
    if args.repeat < 1:
        raise ValueError("--repeat must be at least 1.")
    if args.warmup < 0:
        raise ValueError("--warmup must be 0 or greater.")
    if args.delay < 0:
        raise ValueError("--delay must be 0 or greater.")
    if args.timeout <= 0:
        raise ValueError("--timeout must be greater than 0.")


def _print_result(index: int, total: int, result: object) -> None:
    status = getattr(result, "status")
    elapsed_ms = getattr(result, "elapsed_ms")
    question_id = getattr(result, "question_id")
    if status == "success":
        answerable = getattr(result, "is_answerable")
        confidence = getattr(result, "confidence")
        sources_count = getattr(result, "sources_count")
        confidence_label = (
            f"{confidence:.3f}" if isinstance(confidence, (int, float)) else "n/a"
        )
        print(
            f"[{index}/{total}] {question_id}: ok | "
            f"answerable={answerable} | confidence={confidence_label} | "
            f"sources={sources_count} | {elapsed_ms / 1000:.1f}s",
            flush=True,
        )
    else:
        error = getattr(result, "error")
        print(
            f"[{index}/{total}] {question_id}: ERROR | "
            f"{elapsed_ms / 1000:.1f}s | {error}",
            flush=True,
        )


def main() -> None:
    args = parse_args()
    validate_args(args)
    dataset_path = Path(args.dataset)
    output_path = Path(args.output)
    questions = load_batch_questions(dataset_path)
    selected_questions = questions if args.limit == 0 else questions[: args.limit]

    if not selected_questions:
        raise ValueError("No questions selected for the batch.")

    planned_requests = len(selected_questions) * args.repeat
    results = []
    interrupted = False
    batch_started_at = time.perf_counter()

    config = {
        "dataset": str(dataset_path),
        "base_url": args.base_url,
        "endpoint": args.endpoint,
        "top_k": args.top_k,
        "strategy": args.strategy,
        "reranker_enabled": args.reranker,
        "questions_per_iteration": len(selected_questions),
        "repeat": args.repeat,
        "warmup_requests": min(args.warmup, len(selected_questions)),
        "timeout_seconds": args.timeout,
    }

    timeout = httpx.Timeout(args.timeout)
    with httpx.Client(base_url=args.base_url, timeout=timeout) as client:
        try:
            health_response = client.get(args.health_endpoint)
            health_response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"IRIS API is not available at {args.base_url}: {exc}"
            ) from exc

        runner = QueryBatchRunner(
            client=client,
            endpoint=args.endpoint,
            top_k=args.top_k,
            strategy=args.strategy,
            reranker_enabled=args.reranker,
        )

        warmup_count = min(args.warmup, len(selected_questions))
        if warmup_count:
            print(f"Warm-up: {warmup_count} request(s)...", flush=True)
            for index, question in enumerate(
                selected_questions[:warmup_count], start=1
            ):
                warmup_result = runner.run_question(
                    question=question,
                    sequence=index,
                    iteration=0,
                )
                if warmup_result.status != "success":
                    raise RuntimeError(
                        f"Warm-up failed for {question.id}: {warmup_result.error}"
                    )

        print(
            f"Starting {planned_requests} measured request(s): "
            f"strategy={args.strategy}, reranker={args.reranker}, top_k={args.top_k}",
            flush=True,
        )

        try:
            sequence = 0
            for iteration in range(1, args.repeat + 1):
                for question in selected_questions:
                    sequence += 1
                    result = runner.run_question(
                        question=question,
                        sequence=sequence,
                        iteration=iteration,
                    )
                    results.append(result)
                    _print_result(sequence, planned_requests, result)

                    if result.status == "error" and args.fail_fast:
                        break
                    if args.delay and sequence < planned_requests:
                        time.sleep(args.delay)

                if args.fail_fast and results[-1].status == "error":
                    break
        except KeyboardInterrupt:
            interrupted = True
            print("\nInterrupted. Saving partial results...", flush=True)

    summary = summarize_batch(
        results,
        planned_requests=planned_requests,
        interrupted=interrupted,
    )
    summary["wall_time_seconds"] = round(time.perf_counter() - batch_started_at, 2)
    save_batch_report(
        output_path=output_path,
        config=config,
        summary=summary,
        results=results,
    )

    print("")
    print(f"Completed: {summary['completed_requests']}/{planned_requests}")
    print(f"Successful: {summary['successful_requests']}")
    print(f"Failed: {summary['failed_requests']}")
    print(f"Answer rate: {summary['answer_rate']:.2%}")
    print(f"No-answer rate: {summary['no_answer_rate']:.2%}")
    print(f"Average latency: {summary['average_latency_ms']} ms")
    print(f"P50 latency: {summary['p50_latency_ms']} ms")
    print(f"P95 latency: {summary['p95_latency_ms']} ms")
    print(f"Report saved to: {output_path}")


if __name__ == "__main__":
    main()
