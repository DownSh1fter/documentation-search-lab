"""Command line entry point for trying the lexical search baseline."""

import argparse
from pathlib import Path

from doc_search.data import load_passages
from doc_search.retrieval import TfidfRetriever


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Search the documentation fixture corpus")
    parser.add_argument("query", help="Question or phrase to search for")
    parser.add_argument("--top-k", type=int, default=3, help="Maximum number of results")
    args = parser.parse_args()

    passages = load_passages(PROJECT_ROOT / "data" / "corpus.jsonl")
    retriever = TfidfRetriever(passages)
    results = retriever.search(args.query, top_k=args.top_k)
    if not results:
        print("No matching passages found.")
        return

    for rank, result in enumerate(results, start=1):
        print(f"{rank}. {result.passage.title} (score={result.score:.3f})")
        print(f"   {result.passage.text}")
        print(f"   Source: {result.passage.source_url}")


if __name__ == "__main__":
    main()
