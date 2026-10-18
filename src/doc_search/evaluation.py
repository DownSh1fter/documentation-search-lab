"""Offline retrieval metrics for the labeled question set."""

from collections.abc import Iterable
from typing import Any

from doc_search.retrieval import TfidfRetriever


def recall_at_k(relevant_ids: Iterable[str], retrieved_ids: list[str], k: int) -> float:
    relevant = set(relevant_ids)
    if not relevant:
        raise ValueError("Each evaluation question must have at least one relevant passage")
    return len(relevant.intersection(retrieved_ids[:k])) / len(relevant)


def reciprocal_rank(relevant_ids: Iterable[str], retrieved_ids: list[str]) -> float:
    relevant = set(relevant_ids)
    if not relevant:
        raise ValueError("Each evaluation question must have at least one relevant passage")
    for rank, passage_id in enumerate(retrieved_ids, start=1):
        if passage_id in relevant:
            return 1.0 / rank
    return 0.0


def evaluate_retriever(
    retriever: TfidfRetriever,
    questions: list[dict[str, Any]],
    ks: tuple[int, ...] = (1, 3, 5),
) -> dict[str, Any]:
    if not questions:
        raise ValueError("At least one evaluation question is required")
    if any(k < 1 for k in ks):
        raise ValueError("Every k must be at least 1")

    max_k = max(ks)
    totals = {f"recall@{k}": 0.0 for k in ks}
    totals[f"mrr@{max_k}"] = 0.0
    per_question: list[dict[str, Any]] = []

    known_passage_ids = {passage.id for passage in retriever.passages}
    for question in questions:
        relevant = question["relevant_passage_ids"]
        unknown_ids = set(relevant) - known_passage_ids
        if unknown_ids:
            raise ValueError(
                f"Question {question['id']} refers to unknown passage IDs: "
                f"{', '.join(sorted(unknown_ids))}"
            )

        results = retriever.search(question["question"], top_k=max_k)
        ranked_ids = [result.passage.id for result in results]
        row = {
            "id": question["id"],
            "question": question["question"],
            "question_ru": question.get("question_ru"),
            "relevant_passage_ids": relevant,
            "retrieved_passage_ids": ranked_ids,
            "mrr": reciprocal_rank(relevant, ranked_ids),
        }
        for k in ks:
            score = recall_at_k(relevant, ranked_ids, k)
            row[f"recall@{k}"] = score
            totals[f"recall@{k}"] += score
        totals[f"mrr@{max_k}"] += row["mrr"]
        per_question.append(row)

    count = len(questions)
    metrics = {name: value / count for name, value in totals.items()}
    return {
        "retriever": "tfidf-cosine",
        "corpus_version": "python-docs-3.15.0",
        "question_split": "development-v1",
        "question_count": count,
        "metrics": metrics,
        "per_question": per_question,
    }
