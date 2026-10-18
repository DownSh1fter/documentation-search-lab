"""Load the project's JSON Lines corpus and evaluation questions."""

import json
from pathlib import Path
from typing import Any

from doc_search.retrieval import Passage


def load_passages(path: Path) -> list[Passage]:
    rows = _read_jsonl(path)
    return [Passage(**row) for row in rows]


def load_questions(path: Path) -> list[dict[str, Any]]:
    return _read_jsonl(path)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]
