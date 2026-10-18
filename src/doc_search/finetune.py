"""Fine-tune a sentence embedding model on the labeled retrieval questions."""

import argparse
from pathlib import Path

from doc_search.data import load_passages, load_questions


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def fine_tune(
    passages_path: Path,
    questions_path: Path,
    output: Path,
    base_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    epochs: int = 2,
) -> None:
    try:
        from sentence_transformers import InputExample, SentenceTransformer, losses
        from torch.utils.data import DataLoader
    except ImportError as exc:
        raise RuntimeError(
            "Fine-tuning requires optional dependencies: pip install -e '.[train]'"
        ) from exc

    passages = {p.id: p for p in load_passages(passages_path)}
    questions = load_questions(questions_path)
    examples = []
    for question in questions:
        query = question["question"]
        for passage_id in question["relevant_passage_ids"]:
            passage = passages[passage_id]
            examples.append(
                InputExample(texts=[query, f"{passage.title}. {passage.text}"])
            )
    if not examples:
        raise ValueError("No labeled query-passage pairs found")

    model = SentenceTransformer(base_model)
    loader = DataLoader(examples, shuffle=True, batch_size=min(16, len(examples)))
    loss = losses.MultipleNegativesRankingLoss(model)
    model.fit(
        train_objectives=[(loader, loss)],
        epochs=epochs,
        warmup_steps=max(1, int(len(loader) * epochs * 0.1)),
        output_path=str(output),
        show_progress_bar=True,
    )
    print(f"Fine-tuned model saved to: {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "models" / "retriever")
    parser.add_argument("--base-model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument(
        "--questions",
        type=Path,
        default=PROJECT_ROOT / "data" / "questions-train.jsonl",
        help="Training questions (defaults to the dedicated train split)",
    )
    args = parser.parse_args()
    if args.epochs < 1:
        parser.error("--epochs must be at least 1")
    fine_tune(
        PROJECT_ROOT / "data" / "corpus.jsonl",
        args.questions,
        args.output,
        args.base_model,
        args.epochs,
    )


if __name__ == "__main__":
    main()
