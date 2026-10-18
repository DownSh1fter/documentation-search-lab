"""Run and save the TF-IDF retrieval baseline evaluation."""

import argparse
import json
from pathlib import Path

from doc_search.data import load_passages, load_questions
from doc_search.evaluation import evaluate_retriever
from doc_search.retrieval import SemanticRetriever, TfidfRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the documentation retrieval baseline")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "reports" / "tfidf-baseline.json",
        help="Path for the JSON evaluation report",
    )
    parser.add_argument("--mode", choices=("tfidf", "semantic"), default="tfidf")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument(
        "--questions", type=Path, default=PROJECT_ROOT / "data" / "questions.jsonl"
    )
    parser.add_argument("--split-name", default="development-v1")
    args = parser.parse_args()

    passages = load_passages(PROJECT_ROOT / "data" / "corpus.jsonl")
    questions = load_questions(args.questions)
    retriever = (
        TfidfRetriever(passages)
        if args.mode == "tfidf"
        else SemanticRetriever(passages, args.model)
    )
    report = evaluate_retriever(retriever, questions, question_split=args.split_name)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Corpus passages: {len(passages)}")
    print(f"Evaluation questions: {report['question_count']}")
    for metric, score in report["metrics"].items():
        print(f"{metric}: {score:.3f}")
    missed = [row for row in report["per_question"] if row["recall@5"] == 0.0]
    print(f"Questions with no relevant result in top 5: {len(missed)}")
    print(f"Report saved to: {args.output}")


if __name__ == "__main__":
    main()
