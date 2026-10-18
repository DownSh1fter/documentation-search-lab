"""Simple lexical retrieval baseline based on TF-IDF cosine similarity."""

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class Passage:
    id: str
    title: str
    source_url: str
    text: str


@dataclass(frozen=True)
class SearchResult:
    passage: Passage
    score: float


class TfidfRetriever:
    """Fit a TF-IDF index over passages and return the closest matches."""

    def __init__(self, passages: list[Passage]) -> None:
        if not passages:
            raise ValueError("At least one passage is required")
        self.passages = passages
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(
            f"{passage.title}. {passage.text}" for passage in passages
        )

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        if not query.strip():
            raise ValueError("Query must not be empty")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")

        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).ravel()
        ranked = scores.argsort()[::-1][:top_k]
        return [
            SearchResult(self.passages[index], float(scores[index]))
            for index in ranked
            if scores[index] > 0
        ]


class SemanticRetriever:
    """Dense cosine retrieval using a Sentence Transformers encoder."""

    def __init__(self, passages: list[Passage], model_name: str) -> None:
        if not passages:
            raise ValueError("At least one passage is required")
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "Semantic search requires optional dependencies: pip install -e '.[semantic]'"
            ) from exc
        self.passages = passages
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embeddings = self.model.encode(
            [f"{p.title}. {p.text}" for p in passages], normalize_embeddings=True
        )

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        if not query.strip():
            raise ValueError("Query must not be empty")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        vector = self.model.encode([query], normalize_embeddings=True)[0]
        scores = self.embeddings @ vector
        ranked = scores.argsort()[::-1][:top_k]
        return [SearchResult(self.passages[i], float(scores[i])) for i in ranked]
