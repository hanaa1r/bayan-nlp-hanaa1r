# BENCHMARKS — Bayan

## 1. Claim boundary | حدود الادعاء

- Artefact role: `SYSTEMS_SMOKE`
- Result label: `MEASURED_SMOKE`
- Task: sequence classification — قياس مسار التحسين والخدمة، لا جودة مهمة
- Decision date: 2026-09-01
- Author: متدربة SDA-AIE-211، أكاديمية سدايا

> ⚠️ **لم تُستخدم `PROJECT_ARTIFACT` ولا `MEASURED`** لأن هذا التشغيل على checkpoint مسار Systems Smoke (`google/bert_uncased_L-2_H-128_A-2` برأس غير مدرَّب). الدفتر يُخرج صراحةً `NEXT_REQUIRED_FOR_GATE_D=RERUN_WITH_PROJECT_ARTIFACT_AND_FULL_WORKLOAD`. هذا الملف دليل على أن المسار يعمل، **لا دليل على Gate D**.

## 2. Performance budget — written before candidates

| Constraint | TARGET | Why this matters |
|---|---:|---|
| p95 end-to-end latency | 1000.0 ms | حد أعلى للاستجابة المقبولة على CPU مشترك |
| minimum throughput | 0.1 items/s | حد أدنى يضمن أن المسار لا ينهار تحت الدفعة |
| maximum quality tax | 0.05 | أي تحسين يغيّر أكثر من 5% من التنبؤات مرفوض |
| target device | colab-cpu | بيئة القياس المعلنة؛ لا GPU |

- Commit/time proving budget existed before candidate: الميزانية مطبوعة في خلية `TARGET` قبل أي خلية قياس، ومحفوظة في `reports/benchmark_results.json` تحت `budget_provenance = COURSE_EXAMPLE_FOR_SYSTEMS_SMOKE`

## 3. Reproduction contract

| Field | Value |
|---|---|
| Colab runtime/Python | Google Colab، Python 3.13 |
| Device/provider | CPU، Google Colab |
| CPU/GPU details | colab-cpu؛ لا GPU |
| Library versions | `requirements-day4.txt` |
| Model ID/revision/hash | `google/bert_uncased_L-2_H-128_A-2`، sha256 = `b413ec986cbb7c7c4c3c1a6da3e088299f0848bc6d3eb45af917b821d88774df` |
| Preprocessing version | tokenizer من نفس الـcheckpoint |
| Label map version | `{0: LABEL_0, 1: LABEL_1, 2: LABEL_2}` — رأس غير مدرَّب |
| Workload path/hash | 8 صفوف، sha256 = `1d1d1c3bef8a582931f6a1c1803671e8fe194fc36ae59cdc4f4feca9fc4d6785` |
| Split | workload تجريبي ثابت، لا validation ولا frozen test |
| Examples + AR/EN counts | 8 أمثلة، عربية وإنجليزية |
| Length distribution | p50=18.0، p95=28.95، max=30 |
| Batch size | 4 (dynamic batching: `[(4, 30), (4, 26)]`) |
| Padding/max length | dynamic padding؛ `max_length=96`، `would_truncate=0` |
| Warm-up/repetitions | 5 / 30 |
| Measured boundary | model-only للمقارنة؛ end-to-end (`tokenisation + model`) محفوظ في التقرير |
| Memory method | لم يُقس RSS في هذا التشغيل — راجع القسم 6 |

## 4. Controlled candidates

| ID | Runtime/precision | Only intended change | Artefact hash | Size MiB |
|---|---|---|---|---:|
| A | PyTorch FP32 reference | baseline | `b413ec98…774df` | 16.732 |
| B | ONNX Runtime FP32 | runtime/export فقط | `bayan_model_fp32.onnx` | 16.788 |
| C | ONNX Runtime dynamic INT8 | weight quantisation فقط | `bayan_model_int8.onnx` | 4.287 |

ONNX checker: **PASS**. Quantisation preprocess: **PASS**.

## 5. Parity

| Comparison | max abs logits diff | mean abs diff | prediction agreement | Verdict |
|---|---:|---:|---:|---|
| A vs B | 2.05e-07 | ضمن دقة float32 | **1.000** | **PASS** — الفارق في حدود تمثيل الأرقام |
| A vs C | لم يُقس عدديًا | — | **0.625** | **FAIL** — اختلاف التنبؤ في 3 من 8 |

- Tolerance chosen before inspection: `max_quality_tax = 0.05` من الميزانية، أي `prediction_agreement ≥ 0.95`
- Rationale: التصدير يجب ألا يغيّر السلوك؛ أي انحراف يتجاوز دقة الأرقام يعني تغيّرًا في المخرجات لا في التمثيل فقط.

## 6. Performance results

| ID | p50 ms | p95 ms | p99 ms | items/s | observed peak RSS MiB | speedup vs A |
|---|---:|---:|---:|---:|---:|---:|
| A | راجع التقرير | **37.554** | راجع التقرير | راجع التقرير | لم يُقس | 1.00× |
| B | راجع التقرير | **24.653** | راجع التقرير | راجع التقرير | لم يُقس | **1.52×** |
| C | راجع التقرير | **10.031** | راجع التقرير | راجع التقرير | لم يُقس | **3.74×** |

- كل الأرقام p95 **model-only**، بعد 5 warm-up و30 تكرارًا، 8 عناصر لكل استدعاء.
- **قيد معلوم:** لم يُسجَّل `observed peak RSS` في هذا التشغيل. التفاصيل الكاملة (p50/p99/throughput) في `reports/benchmark_results.json`.

## 7. Quality results

- Primary task metric: **`prediction_agreement_to_fp32_not_task_quality`**
- Evaluation file/split: نفس الـworkload الثابت (8 أمثلة) لكل المرشحين

| ID | Task quality | Quality tax = A − candidate | Small-sample/CI note |
|---|---:|---:|---|
| A | 1.000 (مرجع) | 0 | مرجع بالتعريف |
| B | **1.000** | **0.000** | 8 أمثلة؛ كل مثال = 12.5% |
| C | **0.625** | **0.375** | 8 أمثلة؛ 3 تنبؤات مختلفة |

⚠️ **هذا ليس مقياس جودة مهمة.** الرأس غير مدرَّب، فالمقياس يعبّر عن اتفاق التنبؤ مع المرجع فقط.

## 8. Budget verdict and decision

| Candidate | latency OK | throughput OK | quality OK | Overall |
|---|---|---|---|---|
| B (ONNX FP32) | ✅ | ✅ | ✅ | **budget_met = True** |
| C (ONNX INT8) | ✅ | ✅ | ❌ | **budget_met = False** |

- Selected runtime: **`onnx-fp32`**
- Decision: **ADOPT_ONNX_FP32** — مع وسم `SYSTEMS_SMOKE_NOT_A_SHIP_DECISION`
- Evidence-based reason: ONNX FP32 يخفض p95 من 37.554ms إلى 24.653ms (**1.52×**) بـ`prediction_agreement = 1.000` — تسريع بلا أي تكلفة. INT8 أسرع (3.74×) وأصغر بأربعة أضعاف، لكن `prediction_agreement = 0.625` يعني تكلفة جودة 0.375 — **سبعة أضعاف حد الميزانية 0.05**. الحجم الأصغر والزمن الأقل لا يبرّران فقدان ثلث التنبؤات، فرُفض INT8.
- Known limitation/noise source: 8 أمثلة فقط؛ CPU مشترك في Colab والأزمنة تعتمد على الجلسة؛ لم يُقس throughput تحت تزامن؛ لم يُسجَّل RSS.
- FP32 rollback/reproduction path: مرجع PyTorch FP32 قابل لإعادة الإنشاء من الـcheckpoint العام بالـhash المذكور. **لم تُرفع ملفات `.onnx` ولا أوزان إلى المستودع** — فقط التقارير والـhashes.
- Generated JSON report: `reports/benchmark_results.json`

## 9. Reproduction commands

```bash
# 1. افتح الدفتر في Colab
#    notebooks/08_optimization_serving.ipynb
# 2. ثبّت النسخ
pip install -q -r requirements-day4.txt
# 3. Runtime → Run all من commit ba58eff
# 4. قارن المخرجات مع
#    reports/benchmark_results.json
#    reports/service_smoke.json
```

لا توجد مفاتيح ولا أسرار في أي خطوة.

## 10. Integrity check

- [x] Budget predates candidate results — مطبوع في خلية `TARGET` قبل أي قياس
- [x] Same workload/device/batch/boundary used — نفس الـworkload بـsha256 واحد لكل المرشحين
- [x] Warm-up excluded — 5 تكرارات إحماء مستبعدة
- [x] At least 30 measured repetitions — 30 تكرارًا لكل مرشح
- [ ] p50/p95/p99 and throughput included — **p95 فقط مذكور هنا؛ الباقي في `reports/benchmark_results.json`**
- [ ] Memory wording matches measurement method — **لم يُقس RSS في هذا التشغيل، وهذا مذكور صراحةً**
- [x] Quality tax uses the same examples — نفس الأمثلة الثمانية
- [x] Failed/slower candidates were not hidden — INT8 مرفوض ومذكور بأرقامه كاملة
- [x] Numbers are measured, not copied — كل الأرقام من تشغيلي، موسومة `MEASURED_SMOKE` لا `MEASURED`
- [x] No weights, ONNX artefacts, cache, secrets, or PII committed

## 11. بند مفتوح لـGate D

الدفتر يُخرج: `NEXT_REQUIRED_FOR_GATE_D=RERUN_WITH_PROJECT_ARTIFACT_AND_FULL_WORKLOAD`

**المطلوب لإغلاقه:** استبدال مصدر النموذج بـartefact بيان الفعلي، وworkload كامل بمعرّفات ثابتة، وقياس metric المهمة قبل/بعد بدل `prediction_agreement`، وتسجيل RSS وp50/p99/throughput في هذا الملف 
