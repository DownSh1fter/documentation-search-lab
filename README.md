# Documentation Search Lab

[Русская версия ниже](README.ru.md).

An end-to-end NLP retrieval project with TF-IDF and dense semantic search, a fine-tunable sentence-embedding retriever, and local retrieval-augmented answer generation (RAG) with source links.

## Why this project

This personal learning project is a way to practice practical ML engineering: corpus preparation, a reproducible evaluation set, retrieval metrics, error analysis, an API, and a small demo. We will record measured results with the dataset version and evaluation limits.

## What this project does

Documentation Search Lab helps a user find information in a fixed collection of technical documents. For example, a question such as "How do I open a text file with a specific encoding?" is used to retrieve relevant Python documentation passages. In RAG mode, a local language model then attempts to write an answer from those passages and cite its sources.

| Mode | Purpose | Current access |
| --- | --- | --- |
| TF-IDF | Find passages by lexical overlap between the question and documents | CLI, browser interface, and search API |
| Semantic search | Find passages using sentence embeddings and cosine similarity | CLI |
| RAG | Retrieve evidence and generate an answer with source references using local Qwen | CLI |

Fine-tuning adapts the sentence-embedding retriever on labeled question–passage pairs. It does not fine-tune the Qwen generator. Citation-ID validation checks that cited IDs belong to the supplied evidence; it does not prove that the cited passage supports every claim.

## Where it can be used

Today, the project can be used locally to search the included Python documentation, compare retrieval approaches, and practice data preparation, model adaptation, evaluation, and error analysis. It also provides a portfolio demonstration of an NLP retrieval and RAG workflow.

The following are possible adaptations, rather than ready-made integrations:

| Scenario | Example | Work needed |
| --- | --- | --- |
| Team documentation | Find service descriptions and onboarding instructions | Prepare the corpus, refresh documents, and enforce access permissions where required |
| Product support | Retrieve answers from manuals and FAQs | Add product documents and evaluate representative customer questions |
| QA knowledge search | Find API requirements and expected product behavior | Ingest specifications and check answers against versioned sources |
| Personal technical knowledge base | Search notes and technical guides | Add document loaders and an indexing/update workflow |

The current corpus is a selected subset of Python documentation. Arbitrary PDFs, websites, and corporate knowledge bases are not automatically supported. The browser interface and search API currently expose TF-IDF only; semantic search and RAG are available through the CLI.

RAG remains experimental: the published smoke test does not meet answer-quality and citation-support gates. See [evaluation results](reports/EVALUATION_RESULTS.md) before relying on generated answers. Production use would require broader evaluation, better answer grounding, and operational work such as deployment, monitoring, and access control.

## Current status

The project indexes 206 passages from seven pages of the Python 3.15.0 Tutorial and the built-in `open()` reference. Its 32 English questions have manually labeled relevant passages and Russian translations. Implemented: TF-IDF and dense retrieval, contrastive fine-tuning, and a local RAG pipeline with evidence retrieval, cited generation, and abstention. The current eight-question retrieval holdout shows a small dense-search improvement after fine-tuning, but TF-IDF remains stronger on Recall@1 and MRR@5. The six-case RAG smoke test does not meet its answer-quality or citation gates, so RAG is implemented but not yet validated as a reliable question-answering system. See `reports/EVALUATION_RESULTS.md`.

## Quick start

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
python -m pip install -e .
python scripts/build_corpus.py
python -m doc_search.evaluate
python -m doc_search.cli "How do I read a text file?"
```

### Semantic search, fine-tuning, and RAG

```bash
python -m pip install -e '.[semantic,rag,train]'
python -m doc_search.evaluate --mode semantic --model sentence-transformers/all-MiniLM-L6-v2 --questions data/questions-holdout.jsonl --split-name holdout-v1 --output reports/semantic-holdout.json
python -m doc_search.finetune --questions data/questions-train.jsonl --output models/retriever --epochs 2
python -m doc_search.evaluate --mode tfidf --questions data/questions-holdout.jsonl --split-name holdout-v1 --output reports/tfidf-holdout.json
python -m doc_search.evaluate --mode semantic --model models/retriever --questions data/questions-holdout.jsonl --split-name holdout-v1 --output reports/fine-tuned-holdout.json
python -m doc_search.cli "How do I read a text file?" --mode semantic --model models/retriever
python -m doc_search.cli "How do I read a text file?" --mode rag --model models/retriever
python -m doc_search.evaluate_rag --model models/retriever --answer-model Qwen/Qwen2.5-1.5B-Instruct
```

Semantic search and fine-tuning run locally with Sentence Transformers; the first run downloads the selected base model. Fine-tuning uses the train split with a multiple-negatives ranking objective. RAG retrieves passages and uses a local instruction-tuned Qwen model to generate a concise, cited answer from the evidence only; the pipeline requires valid source IDs and abstains when evidence is weak or the model refuses. RAG dependencies and model weights are downloaded on first use. Do not report a quality gain without comparing evaluation reports on a held-out question split.

The RAG review set currently has six manually curated cases (four answerable and two unanswerable). `reports/RAG_REVIEW.md` defines manual answer/support/citation judgments and provisional smoke-test success gates. Expand and hold out cases before making broad performance claims.

### Web interface

After installing the project, double-click `start-search.bat` on Windows. It opens the search page in your browser. Enter a question in English, choose how many results to show, and select **Find**. Each result shows a documentation passage, its TF-IDF score, and a link to the source page. Keep the console window open while using the app; press `Ctrl+C` there to stop the server.

You can also start the interface from an activated environment with `python -m doc_search.web`, then open `http://127.0.0.1:8000`.

## Planned milestones

1. Define the task, corpus sources, and evaluation format.
2. Measure a lexical retrieval baseline with Recall@k and MRR.
3. Compare implemented dense semantic retrieval against the lexical baseline.
4. Fine-tune on the train split; compare against TF-IDF and the base embedding model on the held-out questions.
5. Generate grounded local RAG answers with source links and abstention.
6. Package the API and web interface for reproducible startup with Docker.

## Evaluation principles

- Keep development questions separate from a final holdout set.
- Compare retrieval changes on the same frozen questions.
- Report retrieval metrics and failure examples; avoid a single accuracy number without context.
- Record the corpus version, model name, configuration, and random seed with results.

## TF-IDF baseline

The baseline uses English TF-IDF with unigrams and bigrams, ranked by cosine similarity. On the current development set:

| Metric | Score |
| --- | ---: |
| Recall@1 | 0.594 |
| Recall@3 | 0.719 |
| Recall@5 | 0.875 |
| MRR@5 | 0.680 |

Four of 32 questions had no relevant passage in the top five. These are development results for a small, manually labeled question set, not a final holdout evaluation. See `reports/` for the saved metrics and error notes.

## Resume-ready summary (implementation scope)

- Built a documentation retrieval pipeline with lexical TF-IDF and dense semantic search using Sentence Transformers; evaluated ranking with Recall@k and MRR.
- Implemented contrastive fine-tuning of sentence embeddings from labeled question-passage pairs, with model export and held-out evaluation (improves over the base dense encoder, but not TF-IDF, on the current eight-question holdout).
- Implemented a local generative RAG pipeline with dense retrieval, evidence-constrained Qwen answer generation, citation-ID validation, and abstention; the six-case smoke test fails answer-quality and citation-support gates, so reliability is not yet established.

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
