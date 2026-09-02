# PROGRESS

## Day 1 — Text Processing, Tokenisation & Attention

- [x] Notebook 01 — `DAY1_NOTEBOOK1_CORE=PASS`
- [x] Notebook 02 — `DAY1_NOTEBOOK2_CORE=PASS`
- [x] Tokenizer decision — [DECISIONS.md](DECISIONS.md)
- [x] `src/` + `tests/` — 79 passed (`PYTHONPATH=src python -m pytest -q`)

**Day 1 = complete** — Gate A

## Day 2 — Classification, NER & QA

- [x] Notebook 03 — `DAY2_NOTEBOOK3_CORE=PASS` (group_overlap = 0، baseline 0.6667 مقابل transformer 1.0000 على validation)
- [x] Notebook 04 — `DAY2_NOTEBOOK4_CORE=PASS` وT4/T5 (NER entity F1 = 1.000 بسياسة هجينة موثقة، QA no-answer = 20/20)
- [x] Day 2 decisions — [DECISIONS.md](DECISIONS.md)
- [x] Gate B commit: `feat: add classification ner and qa pipelines`

**Day 2 = complete** — Gate B

## Day 3 — Arabic NLP, Search & Evaluation

- [x] Notebook 05 — `DAY3_NOTEBOOK5_CORE=PASS` (CAMeL Tools 1.6.0، profile `search/1.0.0`، 4 golden cases، مقارنة mBERT 0.000 مقابل CAMeLBERT-DA 0.667 على Gulf test)
- [x] Notebook 06 — `DAY3_NOTEBOOK6_CORE=PASS` وT7 (Recall@10 = 1.000، MRR@10 = 0.722 بعد re-ranking)
- [x] Notebook 07 — `DAY3_NOTEBOOK7_CORE=PASS` وT8/T9 (MFT = 100%، invariance = 100%، و104 صف مراجعة متغيرات مضبوطة مع إفصاح المصدر)
- [x] Day 3 decisions — [DECISIONS.md](DECISIONS.md)
- [x] [EVALUATION_REPORT.md](EVALUATION_REPORT.md) مكتمل
- [x] التقارير: `reports/search_manifest.json` · `reports/retrieval_metrics.json` · `reports/arabic_model_comparison.json` · `reports/day3_evaluation_fixture.json` · `reports/day3_slice_report.csv` · `reports/day3_error_taxonomy.csv`

**Day 3 = complete** — Gate C

## Day 4 — Optimisation, Serving & Submission

- [x] Notebook 00 — `BAYAN_ENV_READY = True`
- [x] Notebook 08 — `DAY4_NOTEBOOK8_CORE=PASS` على `PROJECT_ARTIFACT` (HTTP p99 = 17.35 ms عند concurrency 16؛ batch speedup = 6.48×)
- [x] [BENCHMARKS.md](BENCHMARKS.md) مكتمل
- [x] Day 4 decisions — [DECISIONS.md](DECISIONS.md)
- [x] [PROJECT_SUMMARY.json](PROJECT_SUMMARY.json) · [SUBMISSION.yml](SUBMISSION.yml)
- [x] [DATA_CARD.md](DATA_CARD.md) · [MODEL_CARD.md](MODEL_CARD.md) · [STUDENT_PROFILE.md](STUDENT_PROFILE.md)
- [x] التقارير: `reports/benchmark_results.json` · `reports/service_smoke.json`
- [x] tag `submission-v1.0`

**Day 4 = complete**

## بنود مفتوحة موثقة

- أحجام التقييم صغيرة واصطناعية ولا تثبت جودة إنتاجية.
- صفوف T9 هي متغيرات مضبوطة لثمانية أخطاء مستقلة، وليست 104 مصادر مستقلة؛ الإفصاح محفوظ في `reports/error_analysis.json`.
- لم يُنفَّذ فحص تشابه نصي آلي للبيانات. موثق في [DATA_CARD.md](DATA_CARD.md).
