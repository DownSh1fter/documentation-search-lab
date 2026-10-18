"""Generate reviewable RAG predictions for the manually curated evaluation set."""

import argparse
import json
from pathlib import Path
from typing import Any

from doc_search.data import load_passages, load_questions
from doc_search.rag import LocalRAG
from doc_search.retrieval import SemanticRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--answer-model", default="Qwen/Qwen2.5-1.5B-Instruct")
    parser.add_argument("--ids", nargs="*", help="Optional case IDs to evaluate")
    parser.add_argument(
        "--output", type=Path, default=PROJECT_ROOT / "reports" / "rag-predictions.jsonl"
    )
    args = parser.parse_args()
    passages = load_passages(PROJECT_ROOT / "data" / "corpus.jsonl")
    cases = load_questions(PROJECT_ROOT / "data" / "rag-evaluation.jsonl")
    if args.ids:
        cases = [case for case in cases if case["id"] in args.ids]
    rag = LocalRAG(SemanticRetriever(passages, args.model), model_name=args.answer_model)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as output:
        for case in cases:
            result = rag.answer(case["question"])
            row: dict[str, Any] = {
                **case,
                "retrieval_model": args.model,
                "answer_model": args.answer_model,
                "answer": result.answer,
                "answer_confidence": result.confidence,
                "raw_model_output": result.raw_answer,
                "retrieved_passage_ids": [item.passage.id for item in result.retrieved],
                "used_passage_ids": [item.passage.id for item in result.sources],
                "sources": [
                    {
                        "id": item.passage.id,
                        "title": item.passage.title,
                        "url": item.passage.source_url,
                        "score": item.score,
                    }
                    for item in result.sources
                ],
                "human_judgment": {
                    "answer_correct": None,
                    "supported_by_sources": None,
                    "citation_correct": None,
                    "abstention_correct": None,
                },
            }
            output.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Generated {len(cases)} predictions for manual review: {args.output}")


if __name__ == "__main__":
    main()
