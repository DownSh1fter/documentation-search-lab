# Documentation Search Lab

[Русская версия ниже](README.ru.md).

An end-to-end text retrieval project. The goal is to compare lexical and semantic search over technical documentation, measure retrieval quality, inspect failures, and serve grounded answers with source links.

## Why this project

This personal learning project is a way to practice practical ML engineering: corpus preparation, a reproducible evaluation set, retrieval metrics, error analysis, an API, and a small demo. We will record measured results with the dataset version and evaluation limits.

## Current status

The current version indexes 198 passages extracted from seven pages of the Python 3.15.0 Tutorial. Its 32 English development questions have manually labeled relevant passages and Russian translations.

## Quick start

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -e .
python scripts/build_corpus.py
python -m doc_search.evaluate
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

## TF-IDF baseline

The baseline uses English TF-IDF with unigrams and bigrams, ranked by cosine similarity. On the current development set:

| Metric | Score |
| --- | ---: |
| Recall@1 | 0.625 |
| Recall@3 | 0.750 |
| Recall@5 | 0.875 |
| MRR@5 | 0.704 |

Four of 32 questions had no relevant passage in the top five. These are development results for a small, manually labeled question set, not a final holdout evaluation. See `reports/` for the saved metrics and error notes.

## Repository map

```text
data/                 source documents and evaluation questions
scripts/              reproducible corpus builder
src/doc_search/       ingestion, retrieval, evaluation, and API code
reports/              saved metrics and error analysis
```

## Data and license

The corpus is downloaded and rebuilt from official Python documentation by `scripts/build_corpus.py`. Sources, version, access date, and license details are tracked in `data/SOURCES.md`.

Code is licensed under MIT. Do not commit private or personal data.

## Language

Project documentation is available in English and Russian. Code, identifiers, and commit messages use English to make the repository easy to review internationally.
