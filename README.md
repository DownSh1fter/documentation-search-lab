# Documentation Search Lab

[Русская версия ниже](README.ru.md).

An end-to-end text retrieval project. The goal is to compare lexical and semantic search over technical documentation, measure retrieval quality, inspect failures, and serve grounded answers with source links.

## Why this project

This personal learning project is a way to practice practical ML engineering: corpus preparation, a reproducible evaluation set, retrieval metrics, error analysis, an API, and a small demo. We will record measured results with the dataset version and evaluation limits.

## Current status

The first runnable milestone is a TF-IDF lexical retriever over a tiny hand-written fixture corpus. The fixture makes the pipeline easy to inspect; it is not a benchmark. We will replace it with real documentation before evaluating search quality.

## Quick start

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m doc_search.cli "How do I read a text file?"
```

## Planned milestones

1. Define the task, corpus sources, and evaluation format.
2. Measure a lexical retrieval baseline with Recall@k and MRR.
3. Add semantic retrieval and compare it on the same questions.
4. Inspect failures and try hybrid retrieval or reranking if useful.
5. Add grounded answer generation with citations and abstention.
6. Serve the system with FastAPI and Docker; document reproducible setup and results.

## Evaluation principles

- Keep development questions separate from a final holdout set.
- Compare retrieval changes on the same frozen questions.
- Report retrieval metrics and failure examples; avoid a single accuracy number without context.
- Record the corpus version, model name, configuration, and random seed with results.

## Repository map

```text
data/                 source documents and evaluation questions
src/doc_search/       ingestion, retrieval, evaluation, and API code
reports/              saved metrics and error analysis
```

## Data and license

The current `data/corpus.jsonl` contains original learning-fixture passages that paraphrase concepts from Python documentation. It is not a benchmark. Corpus source URLs and license details are tracked in `data/SOURCES.md`.

Code is licensed under MIT. Do not commit private or personal data.

## Language

Project documentation is available in English and Russian. Code, identifiers, and commit messages use English to make the repository easy to review internationally.
