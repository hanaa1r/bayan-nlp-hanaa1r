# Bayan | بيان — Bilingual Applied NLP Capstone

مشروع تعليمي ثنائي اللغة يستقبل ملاحظة قصيرة بالعربية أو الإنجليزية، يحمي البيانات الشخصية ويعالج النص، ثم ينفذ تصنيف الموضوع والمشاعر، واستخراج الكيانات، والإجابة الاستخراجية، والبحث الدلالي. يعرض المسار النهائي النتائج من خلال خدمة FastAPI مختبرة.

نُفذ هذا المشروع ضمن برنامج **SDA-AIE-211 — Natural Language Processing with Transformers**، بإعداد وتقديم المدربة **ميعاد المري**، ضمن برامج **أكاديمية سدايا**. حساب الأكاديمية: [SDAIAAcademy](https://github.com/SDAIAAcademy).

## المشكلة والقيمة

تصل ملاحظات المستفيدين بلغتين وبصيغ متفاوتة، وقد تحتوي بيانات تعريفية أو لهجة عربية. يوحّد بيان معالجة هذه النصوص ويقدم مخرجات قابلة للتقييم بدل الاعتماد على نموذج أسود الصندوق. المستخدم المقصود هو المراجع أو المطور الذي يريد تجربة مسار NLP تعليمي قابل لإعادة التشغيل.

المشروع **لا** يمثل نظامًا حكوميًا حقيقيًا، ولا يستخدم شكاوى أو بيانات شخصية حقيقية، ولا يدّعي جاهزية إنتاجية أو تعميم النتائج خارج البيانات الاصطناعية المقاسة.

## المهام

| المهمة | التنفيذ والدليل |
|---|---|
| المعالجة والخصوصية | NFC، فك HTML، إزالة الوسوم والتطويل، توحيد المسافات، وإخفاء البريد والهاتف مع الاحتفاظ بنسخة عرض آمنة |
| Topic classification | TF-IDF baseline ومصنف Transformer متعدد اللغات مع Macro-F1 |
| Sentiment classification | رأس مستقل وlabel map مستقلة لفئات positive/negative/neutral |
| NER | محاذاة BIO مع subwords وحساب strict entity-level F1 |
| Extractive QA | قيود span وoffsets وسياسة no-answer قابلة للتفسير |
| Semantic search | sentence embeddings وFAISS واسترجاع ثم re-ranking |
| Evaluation | مقاييس وشرائح وCI واختبارات سلوكية وتصنيف أخطاء |
| Serving | ONNX/INT8 candidates وخدمة FastAPI وstartup canaries |

## التثبيت والتشغيل

المسار الموصى به هو Google Colab CPU وتشغيل الدفاتر بالترتيب من `00` إلى `08`:

```bash
git clone https://github.com/hanaa1r/bayan-nlp-hanaa1r.git
cd bayan-nlp-hanaa1r
python -m pip install -r requirements-day1.txt
python -m pip install -r requirements-day2.txt
python -m pip install -r requirements-day3.txt
python -m pip install -r requirements-day4.txt
PYTHONPATH=src python -m pytest -q
python scripts/validate_submission.py --require-tag
```

شغّل كل ملف في `notebooks/` داخل Colab باستخدام **Runtime → Run all**. يفضّل تنفيذ دفاتر النماذج والبحث وONNX في جلسات نظيفة منفصلة ضمن حد ذاكرة Colab المجاني.

## مثال الاستخدام

```python
from bayan.preprocessing import prepare_text

result = prepare_text("تواصلوا معي على user@example.com بخصوص موعد العيادة")
print(result.model_text)  # البريد مخفي قبل دخوله إلى النموذج
```

عقد الخدمة النهائي:

```text
GET  /health
POST /v1/classify  {"text": "تأخر موعد العيادة", "language": "ar"}
```

تُرفض المدخلات الفارغة واللغات غير المدعومة بالحالة HTTP 422.

## النتائج المثبتة في submission-v1.0

هذه نتائج Smoke صغيرة وليست ادعاء اجتياز للحزمة الرسمية:

| المهمة | النتيجة | الحد |
|---|---:|---|
| Topic Macro-F1 | 0.867 | test اصطناعي، n=8 |
| NER strict entity-F1 | 0.571 | 4 كيانات فقط |
| Retrieval Recall@3 / MRR@3 | 1.000 / 0.667 | 6 استعلامات |
| ONNX FP32 parity | 1.000 | Systems Smoke |
| الاختبارات الآلية | 79 passed | CPU محلي |

لن يُحدّث هذا القسم إلى نتائج `PROJECT_ARTIFACT` إلا بعد تشغيل الدفتر النهائي فعليًا وحفظ البيئة والتاريخ والـcommit والـreports الناتجة.

## بنية المستودع

```text
data/sample/       بيانات بيان الاصطناعية
notebooks/         دفاتر 00–08 ودفتر التجميع
src/bayan/         وحدات المعالجة والمقاييس والبحث والخدمة
tests/             اختبارات الوحدة والعقود
reports/           تقارير القياس الصغيرة القابلة للفحص
scripts/           الفاحص وأوامر توليد الأدلة
```

ملفات التوثيق الرئيسة: [DATA_CARD.md](DATA_CARD.md)، [MODEL_CARD.md](MODEL_CARD.md)، [EVALUATION_REPORT.md](EVALUATION_REPORT.md)، [BENCHMARKS.md](BENCHMARKS.md)، [DECISIONS.md](DECISIONS.md)، و[PROGRESS.md](PROGRESS.md).

## القيود

- البيانات اصطناعية وصغيرة، وبعض الشرائح لا تتجاوز بضعة أمثلة.
- نتائج الدفاتر المرجعية `MEASURED_SMOKE` لا تساوي نتائج حزمة التقييم الرسمية.
- لا تُرفع الأوزان أو ملفات ONNX إلى GitHub؛ يعاد إنشاؤها من checkpoint موثق.
- زمن Colab CPU يتأثر بالجهاز المشترك ولا يمثل زمن إنتاج.
- يلزم تشغيل `PROJECT_MODE=True` في دفتر 08 باستخدام نموذج بيان الفعلي قبل إعلان Gate D.

## النزاهة وإعادة الإنتاج

جميع البيانات المرفوعة اصطناعية، ولا توجد أسرار أو أوزان أو PII حقيقية. لا تُنسب أرقام الدفاتر المرجعية إلى المشروع. كل نتيجة نهائية يجب أن تتضمن نوع الدليل، البيئة، التاريخ، وcommit SHA، وأن تُنتج من تشغيل فعلي دون تعديل frozen test بعد الاطلاع عليه.

## الشكر والبرنامج

الشكر لأكاديمية سدايا والمدربة ميعاد المري على إعداد برنامج SDA-AIE-211 وحزمة مشروع بيان التعليمية.
