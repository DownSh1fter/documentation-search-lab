# Evaluation results

Run date: 2026-10-19. Corpus: 206 passages from seven Python 3.15.0 Tutorial pages plus the built-in `open()` reference. The retrieval holdout has eight questions, excluded from the 24-question fine-tuning set. Metrics below are preliminary because the holdout is very small.

## Development retrieval

| Model | Questions | Recall@1 | Recall@3 | Recall@5 | MRR@5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| TF-IDF | 32 | 0.594 | 0.719 | 0.875 | 0.680 |
| Base `all-MiniLM-L6-v2` | 32 | 0.531 | 0.781 | 0.875 | 0.674 |

## Retrieval holdout

| Model | Questions | Recall@1 | Recall@3 | Recall@5 | MRR@5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| TF-IDF | 8 | 0.875 | 0.875 | 0.875 | 0.875 |
| Base `all-MiniLM-L6-v2` | 8 | 0.625 | 1.000 | 1.000 | 0.792 |
| Fine-tuned `all-MiniLM-L6-v2` | 8 | 0.750 | 1.000 | 1.000 | 0.854 |

Fine-tuning improved dense retrieval over the base encoder on this holdout, but it did not beat TF-IDF on Recall@1 or MRR@5. The retrieval success gate (higher MRR@5 and Recall@5 than TF-IDF without a Recall@1 regression) is **not met**. Do not present the result as a general fine-tuning improvement.

## RAG smoke test

Reviewed predictions are in `rag-finetuned-predictions.jsonl`. The run used the fine-tuned retriever and `Qwen/Qwen2.5-1.5B-Instruct` on CPU. The six-case set was used during prompt/context development, so it is exploratory rather than an independent benchmark.

| Check | Result | Provisional gate | Status |
| --- | ---: | ---: | --- |
| Answerable questions with a gold passage in top 5 | 3/4 | 4/4 | Fail |
| Answer correct and complete on answerable questions | 1/4 | at least 3/4 | Fail |
| Claims supported by retrieved passages | 2/4 | at least 3/4 | Fail |
| Citation directly supports answer on answerable questions | 1/4 | at least 3/4 | Fail |
| Correct refusal on unanswerable questions | 2/2 | 2/2 | Pass |

Manual review: `rag001` is correct and supported; `rag002` gives a partly useful but incomplete answer and cites an irrelevant passage; `rag003` adds an incorrect claim about runtime exceptions; `rag004` refuses despite a directly relevant stack passage; both unanswerable cases are refused. The open-encoding gold passage is retrieved at rank 6 rather than in the top 5.

The RAG success gate is **not met**. The pipeline is implemented, but answer quality, direct citation grounding, and retrieval coverage need improvement before describing it as a successful question-answering system. A CPU run of the six-case set takes several minutes with the current local generator. Larger-scale claims also require a larger, frozen test set and independent review.
