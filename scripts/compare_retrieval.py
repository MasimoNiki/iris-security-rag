from __future__ import annotations

import argparse
from pathlib import Path

from app.services.evaluation.dataset import load_golden_questions
from app.services.evaluation.retrieval_comparison import (
    RETRIEVAL_PROFILES,
    evaluate_retrieval_strategy,
    save_retrieval_comparison,
    warm_up_retrieval_profile,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare dense, hybrid, and hybrid + reranker without running an LLM."
        ),
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
        "--strategies",
        nargs="+",
        choices=RETRIEVAL_PROFILES,
        default=list(RETRIEVAL_PROFILES),
        help="Retrieval profiles to compare.",
    )
    parser.add_argument(
        "--output",
        default="data/eval/retrieval_comparison.json",
        help="Path for the detailed comparison report.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    questions = load_golden_questions(Path(args.dataset))
    answerable_questions = [question for question in questions if question.answerable]
    if not answerable_questions:
        raise ValueError("The evaluation dataset has no answerable questions.")

    summaries = []
    results_by_strategy = {}

    for strategy in args.strategies:
        print("")
        print(f"Warming up profile: {strategy}")
        warmup_latency_ms = warm_up_retrieval_profile(
            profile=strategy,
            query=answerable_questions[0].question,
            top_k=args.top_k,
        )
        print(f"Warm-up latency: {warmup_latency_ms:.0f} ms")

        summary, results = evaluate_retrieval_strategy(
            questions=questions,
            strategy=strategy,
            top_k=args.top_k,
        )
        summaries.append(summary)
        results_by_strategy[strategy] = results

        print("")
        print(f"Strategy: {strategy}")
        print(f"Document Hit@{args.top_k}: {summary.document_hit_at_k:.2f}")
        print(f"Content Hit@{args.top_k}: {summary.content_hit_at_k:.2f}")
        print(f"Keyword Recall@{args.top_k}: {summary.keyword_recall_at_k:.2f}")
        print(f"Primary MRR: {summary.primary_mrr:.2f}")
        print(f"Document MRR: {summary.document_mrr:.2f}")
        print(f"Content MRR: {summary.content_mrr:.2f}")
        print(f"Average retrieval latency: {summary.average_latency_ms:.0f} ms")
        if strategy == "hybrid_reranked":
            print(
                "Reranker applied: "
                f"{summary.reranker_applied_rate * 100:.0f}% of questions"
            )

    output_path = Path(args.output)
    save_retrieval_comparison(
        output_path=output_path,
        summaries=summaries,
        results_by_strategy=results_by_strategy,
    )
    print("")
    print(f"Detailed comparison saved to: {output_path}")


if __name__ == "__main__":
    main()
