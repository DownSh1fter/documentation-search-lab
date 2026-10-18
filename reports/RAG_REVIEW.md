# RAG evaluation protocol

`data/rag-evaluation.jsonl` contains six manually curated cases: four answerable questions and two questions outside the selected corpus. This is a smoke-test set, not a statistically reliable benchmark.

Generate predictions with the fine-tuned retriever and local Qwen generator:

```bash
python -m doc_search.evaluate_rag --model models/retriever --answer-model Qwen/Qwen2.5-1.5B-Instruct --output reports/rag-finetuned-predictions.jsonl
```

The reviewed run is `reports/rag-finetuned-predictions.jsonl`. It records model names, raw model output, retrieved passages, and human judgments. Regenerating the file resets those judgments to `null`, so preserve a reviewed copy before running evaluation again. Review fields:

- `answer_correct`: the answer is factually correct and sufficiently complete.
- `supported_by_sources`: retrieved passages support every factual claim.
- `citation_correct`: cited passages directly support the answer.
- `abstention_correct`: the system answers an answerable question or refuses an unanswerable one.

Report answer correctness, source support, citation correctness, correct abstention, and retrieval Recall@k separately. Do not combine them into one score. Provisional smoke-test gates are: all four answerable cases retrieve a gold passage in the top 5; at least 3/4 answers are correct and supported; both unanswerable cases are correctly refused. These are screening criteria, not a production benchmark. Add more questions and use a separate holdout before making broad quality claims. Current judgments and pass/fail status are in `reports/EVALUATION_RESULTS.md`.
