# BENCHMARKS — Bayan

## 1. Claim boundary | حدود الادعاء

- Artefact role: `SYSTEMS_SMOKE`
- Result label: `MEASURED_SMOKE`
- Task: sequence classification — قياس مسار التحسين والخدمة، لا جودة مهمة
- Decision date: 2026-09-01
- Author: هناء راشد الجهني

> ⚠️ لم تُستخدم `PROJECT_ARTIFACT` ولا `MEASURED` لأن هذا التشغيل على checkpoint مسار Systems Smoke (`google/bert_uncased_L-2_H-128_A-2` برأس غير مدرَّب). الدفتر يُخرج صراحةً `NEXT_REQUIRED_FOR_GATE_D=RERUN_WITH_PROJECT_ARTIFACT_AND_FULL_WORKLOAD`.

## 2. Performance budget — written before candidates

| Constraint | TARGET | Why this matters |
|---|---:|---|
| p95 end-to-end latency | 1000.0 ms | حد أعلى للاستجابة المقبولة على CPU مشترك |
| minimum throughput | 0.1 items/s | حد أدنى يضمن أن المسار لا ينهار تحت الدفعة |
| maximum quality tax | 0.05 | أي تحسين يغيّر أكثر من 5% من التنبؤات مرفوض |
| target device | colab-cpu | بيئة القياس المعلنة؛ لا GPU |

- Commit/time proving budget existed before candidate: الميزانية مطبوعة في خلية `TARGET` قبل أي خلية قياس، وموسومة `budget_provenance = COURSE_EXAMPLE_FOR_SYSTEMS_SMOKE` في `reports/benchmark_results.json`

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
| Batch size | 4 — dynamic batching `[(4, 30), (4, 26)]` |
| Padding/max length | dynamic padding؛ `max_length=96`، `would_truncate=0` |
| Warm-up/repetitions | 5 / 30 |
| Measured boundary | model-only للمقارنة؛ end-to-end محفوظ في التقرير |
| Memory method | process RSS start and observed peak (تقريبي) |

## 4. Controlled candidates

| ID | Runtime/precision | Only intended change | Artefact hash | Size MiB |
|---|---|---|---|---:|
| A | PyTorch FP32 reference | baseline | `b413ec98…774df` | 16.732 |
| B | ONNX Runtime FP32 | runtime/export فقط | `bayan_model_fp32.onnx` | 16.788 |
| C | ONNX Runtime dynamic INT8 | weight quantisation فقط | `bayan_model_int8.onnx` | 4.287 |

ONNX checker: PASS. Quantisation preprocess: PASS.

## 5. Parity

| Comparison | max abs logits diff | mean abs diff | prediction agreement | Verdict |
|---|---:|---:|---:|---|
| A vs B | 2.05e-07 | 5.63e-08 | 1.000 | PASS — الفارق في حدود دقة float32 |
| A vs C | 0.0240 | 0.0099 | 0.625 | FAIL — اختلاف التنبؤ في 3 من 8 |

- Tolerance chosen before inspection: `max_quality_tax = 0.05` من الميزانية، أي `prediction_agreement ≥ 0.95`
- Rationale: التصدير يجب ألا يغيّر السلوك؛ أي انحراف يتجاوز دقة الأرقام يعني تغيّرًا في المخرجات لا في التمثيل.

## 6. Performance results

| ID | p50 ms | p95 ms | p99 ms | items/s | observed peak RSS MiB | speedup vs A |
|---|---:|---:|---:|---:|---:|---:|
| A | 19.283 | 37.554 | 40.656 | 357.76 | 658.01 | 1.00× |
| B | 8.372 | 24.653 | 28.388 | 700.66 | 746.94 | 1.52× |
| C | 6.761 | 10.031 | 14.329 | 1081.55 | 748.11 | 3.74× |

كل الأرقام **model-only**، بعد 5 warm-up و30 تكرارًا، batch=4، 8 عناصر لكل استدعاء.

**قياس end-to-end لـPyTorch** (tokenisation + model): p50 = 18.253، p95 = 50.262، p99 = 61.768، throughput = 330.48 items/s. الفارق بين 37.554 (model-only) و50.262 (end-to-end) عند p95 يبيّن أن **الترميز يضيف ~34% إلى الذيل** — وهذا ما يخفيه قياس النموذج وحده.

**البيئة:** Python 3.13.15، torch 2.11.0+cpu، onnx 1.22.0، onnxruntime 1.29.0، CPUExecutionProvider.

## 7. Quality results

- Primary task metric: `prediction_agreement_to_fp32_not_task_quality`
- Evaluation file/split: نفس الـworkload الثابت (8 أمثلة) لكل المرشحين

| ID | Task quality | Quality tax = A − candidate | Small-sample/CI note |
|---|---:|---:|---|
| A | 1.000 (مرجع) | 0 | مرجع بالتعريف |
| B | 1.000 | 0.000 | 8 أمثلة؛ كل مثال = 12.5% |
| C | 0.625 | 0.375 | 8 أمثلة؛ 3 تنبؤات مختلفة |

⚠️ ليس مقياس جودة مهمة — الرأس غير مدرَّب.

## 8. Budget verdict and decision

| Candidate | latency OK | throughput OK | quality OK | Overall |
|---|---|---|---|---|
| B | ✅ | ✅ | ✅ | budget_met = True |
| C | ✅ | ✅ | ❌ | budget_met = False |

- Selected runtime: `onnx-fp32`
- Decision: **ADOPT_ONNX_FP32** — مع وسم `SYSTEMS_SMOKE_NOT_A_SHIP_DECISION`
- Evidence-based reason: ONNX FP32 يخفض p95 من 37.554ms إلى 24.653ms (1.52×) بـ`prediction_agreement = 1.000` — تسريع بلا تكلفة. INT8 أسرع 3.74× وأصغر بأربعة أضعاف لكن `agreement = 0.625` يعني تكلفة 0.375، أي سبعة أضعاف حد الميزانية. **حجم الملف ليس مقياس جودة.**
- Known limitation/noise source: 8 أمثلة؛ CPU مشترك في Colab؛ لم يُقس throughput تحت تزامن.
- **RSS لا يميّز المرشحين:** الفروق بين 658 و747 و748 MiB تعكس تراكم المكتبات المحمَّلة في العملية (ORT محمَّل بعد PyTorch)، لا استهلاك المرشح نفسه. `rss_observed_delta` قريب من الصفر لـONNX. القياس تقريبي بطبيعته ولا يصلح لمقارنة بصمة الذاكرة بين المحركات.
- FP32 rollback/reproduction path: مرجع PyTorch قابل لإعادة الإنشاء من الـcheckpoint العام بالـhash المذكور. لم تُرفع ملفات `.onnx` ولا أوزان.
- Generated JSON report: `reports/benchmark_results.json`

## 9. Reproduction commands

```bash
# افتح notebooks/08_optimization_serving.ipynb في Colab
pip install -q -r requirements-day4.txt
# Runtime → Run all من commit ba58eff
# قارن مع reports/benchmark_results.json و reports/service_smoke.json

10. Integrity check
 Budget predates candidate results.
 Same workload/device/batch/boundary used.
 Warm-up excluded.
 At least 30 measured repetitions or limitation explained.
 p50/p95/p99 and throughput included.
 Memory wording matches measurement method — process RSS start and observed peak; approximate
 Quality tax uses the same examples.
 Failed/slower candidates were not hidden.
 Numbers are measured, not copied — موسومة MEASURED_SMOKE
 No weights, ONNX artefacts, cache, secrets, or PII committed.
11. بند مفتوح لـGate D
NEXT_REQUIRED_FOR_GATE_D=RERUN_WITH_PROJECT_ARTIFACT_AND_FULL_WORKLOAD — إعادة التشغيل بنموذج بيان الفعلي وworkload كامل، مع metric مهمة حقيقي وتسجيل RSS. لم يُنفَّذ ضمن الوقت المتاح، موثق كنقص معلوم.
