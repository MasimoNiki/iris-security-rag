from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from app.services.evaluation.dataset import load_golden_questions
from app.services.evaluation.runner import EvaluationRunner, save_eval_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run IRIS SOC RAG evaluation.",
    )
    parser.add_argument(
        "--dataset",
        default="data/eval/golden_questions.yml",
        help="Path to evaluation dataset.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of retrieved chunks to evaluate.",
    )
    parser.add_argument(
        "--retrieval-strategy",
        choices=("dense", "hybrid"),
        default=None,
        help="Override RETRIEVAL_STRATEGY for this evaluation run.",
    )
    parser.add_argument(
        "--reranker",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=(
            "Enable or disable reranking for this run. Defaults to RERANKER_ENABLED."
        ),
    )
    parser.add_argument(
        "--no-answer-threshold",
        type=float,
        default=0.01,
        help=(
            "Treat generation confidence at or below this value as "
            "a no-answer response."
        ),
    )
    parser.add_argument(
        "--output",
        default="data/eval/latest_eval_results.json",
        help="Path to save the detailed evaluation report.",
    )
    parser.add_argument(
        "--baseline-output",
        default=None,
        help=(
            "Optional additional path for an immutable baseline copy. "
            "The command refuses to overwrite it by default."
        ),
    )
    parser.add_argument(
        "--overwrite-baseline",
        action="store_true",
        help="Allow replacing an existing --baseline-output file.",
    )

    return parser.parse_args()


def _save_baseline_copy(
    *,
    report_path: Path,
    baseline_path: Path,
    overwrite: bool,
) -> None:
    if report_path.resolve() == baseline_path.resolve():
        raise ValueError(
            "--baseline-output must be different from --output.",
        )

    if baseline_path.exists() and not overwrite:
        raise FileExistsError(
            f"Baseline already exists: {baseline_path}. "
            "Choose another path or pass --overwrite-baseline.",
        )

    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(report_path, baseline_path)


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    output_path = Path(args.output)
    questions = load_golden_questions(dataset_path)
    runner = EvaluationRunner(
        top_k=args.top_k,
        no_answer_threshold=args.no_answer_threshold,
        retrieval_strategy=args.retrieval_strategy,
        reranker_enabled=args.reranker,
    )
    summary, results = runner.run(questions)

    save_eval_report(
        output_path=output_path,
        summary=summary,
        results=results,
    )

    baseline_path = Path(args.baseline_output) if args.baseline_output else None

    if baseline_path is not None:
        _save_baseline_copy(
            report_path=output_path,
            baseline_path=baseline_path,
            overwrite=args.overwrite_baseline,
        )

    print(
        "Total questions: "
        f"{summary.total_questions} "
        f"(answerable: {summary.answerable_questions}, "
        f"unanswerable: {summary.unanswerable_questions})"
    )
    print(f"Retrieval strategy: {summary.retrieval_strategy}")
    print(f"Reranker enabled: {summary.reranker_enabled}")
    if summary.reranker_enabled:
        print(
            f"Reranker applied: {summary.reranker_applied_rate * 100:.0f}% of questions"
        )
    print(f"Primary Hit@{summary.top_k}: {summary.hit_at_k:.2f}")
    print(f"Document Hit@{summary.top_k}: {summary.document_hit_at_k:.2f}")
    print(f"Content Hit@{summary.top_k}: {summary.content_hit_at_k:.2f}")
    print(f"Keyword Recall@{summary.top_k}: {summary.recall_at_k:.2f}")
    print(f"Primary MRR: {summary.mrr:.2f}")
    print(f"Document MRR: {summary.document_mrr:.2f}")
    print(f"Content MRR: {summary.content_mrr:.2f}")
    print(f"Average latency: {summary.average_latency_ms:.0f} ms")
    print(f"Answerability accuracy: {summary.answerability_accuracy:.2f}")
    print(f"Unanswerable rejection rate: {summary.unanswerable_rejection_rate:.2f}")
    print(f"Answer has sources rate: {summary.answer_has_sources_rate:.2f}")
    print(f"No-answer rate: {summary.no_answer_rate:.2f}")
    print(f"Detailed report saved to: {output_path}")

    if baseline_path is not None:
        print(f"Baseline copy saved to: {baseline_path}")

    failed_retrieval = [
        result for result in results if result.answerable and not result.hit
    ]
    missed_content = [
        result
        for result in results
        if result.answerable
        and result.expected_source_keywords
        and not result.content_hit
    ]
    unsafe_answers = [
        result for result in results if not result.answerable and not result.no_answer
    ]

    if failed_retrieval:
        print("")
        print("Failed answerable retrieval questions:")

        for result in failed_retrieval[:10]:
            print(
                f"- {result.question_id}: {result.question} "
                f"| expected_external_ids="
                f"{result.expected_external_ids} "
                f"| expected_local_paths={result.expected_local_paths}"
            )

    if missed_content:
        print("")
        print("Document found but expected content was not found:")

        for result in missed_content[:10]:
            print(
                f"- {result.question_id}: {result.question} "
                f"| matched_keywords={result.matched_keywords}"
            )

    if unsafe_answers:
        print("")
        print("Unanswerable questions that received an answer:")

        for result in unsafe_answers[:10]:
            print(f"- {result.question_id}: {result.question}")


if __name__ == "__main__":
    main()
