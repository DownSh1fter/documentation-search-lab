"""Evidence-grounded retrieval-augmented answer generation over documentation."""

import re
from dataclasses import dataclass
from typing import Any

from doc_search.retrieval import SearchResult


@dataclass(frozen=True)
class GroundedAnswer:
    answer: str
    sources: list[SearchResult]
    retrieved: list[SearchResult]
    confidence: float
    raw_answer: str = ""


class LocalRAG:
    """Retrieve a small evidence context and generate locally cited answers."""

    def __init__(
        self,
        retriever: Any,
        model_name: str = "Qwen/Qwen2.5-1.5B-Instruct",
        min_evidence_score: float = 0.2,
    ) -> None:
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError(
                "Local RAG requires optional dependencies: pip install -e '.[rag]'"
            ) from exc
        self.retriever = retriever
        self.generator = pipeline("text-generation", model=model_name)
        self.min_evidence_score = min_evidence_score

    def answer(self, query: str, top_k: int = 10) -> GroundedAnswer:
        retrieved = self.retriever.search(query, top_k=top_k)
        evidence = self._select_evidence(query, retrieved)
        if not evidence:
            return self._abstain(retrieved)

        context = "\n\n".join(
            f"[{item.passage.id}] {text}" for item, text, _ in evidence
        )
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Python documentation question-answering system. First check "
                    "whether the evidence explicitly contains the requested information. "
                    "When it does, answer directly in one concise sentence using only those "
                    "facts and finish with the ID of the supporting evidence in square brackets. "
                    "Do not refuse an answer that is stated in the evidence. When the evidence "
                    "does not state the answer, reply exactly NOT_ANSWERED. Do not add explanations."
                ),
            },
            {"role": "user", "content": f"Question: {query}\nEvidence:\n{context}"},
        ]
        generated = self.generator(
            messages,
            max_new_tokens=72,
            do_sample=False,
            return_full_text=False,
        )[0]["generated_text"]
        if isinstance(generated, list):
            generated = generated[-1].get("content", "")
        answer = str(generated).strip()
        if not answer or "NOT_ANSWERED" in answer.upper():
            return self._abstain(retrieved, answer)

        ids = set(re.findall(r"\[([^\[\]]+)\]", answer))
        source_ids = {item.passage.id for item, _, _ in evidence}
        if not ids or not ids.issubset(source_ids):
            return self._abstain(retrieved, answer)
        sources = list(
            {
                result.passage.id: result
                for result, _, _ in evidence
                if result.passage.id in ids
            }.values()
        )
        confidence = max(score for result, _, score in evidence if result.passage.id in ids)
        return GroundedAnswer(answer, sources, retrieved, confidence, answer)

    def _select_evidence(
        self, query: str, retrieved: list[SearchResult], max_passages: int = 5
    ) -> list[tuple[SearchResult, str, float]]:
        del query  # Retrieval already ranked the full passages for this query.
        return [
            (result, result.passage.text[:1600], result.score)
            for result in retrieved[:max_passages]
            if result.score >= self.min_evidence_score
        ]

    @staticmethod
    def _abstain(retrieved: list[SearchResult], raw_answer: str = "") -> GroundedAnswer:
        return GroundedAnswer(
            "I could not find enough supporting documentation to answer this question.",
            [],
            retrieved,
            0.0,
            raw_answer,
        )
