# Bayan Model Card

هذا الملف يوثّق خمسة artefacts في أقسام مستقلة. لم تُدمج مقاييس checkpoints مختلفة في صف واحد.

---

## 1. Topic classification

### Model details
- Name/version: `bayan-topic-classifier` / v0.1 (SYSTEMS_SMOKE)
- Base checkpoint: `distilbert/distilbert-base-multilingual-cased`
- Task: تصنيف الموضوع إلى أربع فئات — digital_service، health، permit، transport
- License/source: Apache-2.0، Hugging Face
- Commit SHA: `ba58eff`
- Owner/contact role: متدربة في برنامج SDA-AIE-211، أكاديمية سدايا

### Intended use
- الاستخدام المقصود: تصنيف ملاحظات مستفيدين قصيرة بالعربية أو الإنجليزية إلى فئة خدمة، لأغراض تعليمية داخل مشروع بيان.
- المستخدمون المقصودون: المتدربة والمقيّمون في البرنامج.
- خارج النطاق: أي استخدام تشغيلي أو حكومي حقيقي، أي قرار يمسّ مستفيدًا، أي لغة أو لهجة خارج ما قيس، وأي فئة خارج الأربع المذكورة.

### Data and preprocessing
- Dataset ID/version: `bayan_day2_classification.csv` — 40 صفًا اصطناعيًا من مستودع الدورة
- Languages/variants: عربية (MSA وGulf) وإنجليزية
- Split strategy: split مجمّد في الملف — train 24 / validation 8 / test 8، مع `group_id` يمنع تسرب الحالات المتشابهة. `validate_splits` تتحقق أن كل مجموعة في split واحد — النتيجة **group_overlap = 0** على 20 مجموعة.
- PII policy: بيانات اصطناعية بالكامل؛ أنماط البريد والهاتف التعليمية تُخفى إلى `<EMAIL>` و`<PHONE>` قبل التدريب.
- Preprocessing profile/version/backend: محافظ — NFC، فك HTML، حذف الوسوم، حذف التطويل، توحيد المسافات، إخفاء PII. بلا حذف تشكيل ولا توحيد ألف.
- Tokenizer: من نفس الـcheckpoint، `max_length=64`

### Evaluation

| metric/slice | n | result | uncertainty | evidence file |
|---|---:|---:|---|---|
| Macro-F1 (test) | 8 | 0.867 | بذرة واحدة، بلا CI | `notebooks/03_text_classification.ipynb` |
| Accuracy (test) | 8 | 0.875 | بذرة واحدة | نفس الدفتر |
| Macro-F1 (validation) | 8 | 1.000 | استُخدم لاختيار الحقبة | نفس الدفتر |
| TF-IDF baseline (test) | 8 | 0.733 | بذرة واحدة | نفس الدفتر |
| Gulf frozen test (mBERT) | 4 | 0.000 | بذرة واحدة | `reports/arabic_model_comparison.json` |
| Gulf frozen test (CAMeLBERT-DA) | 4 | 0.667 | بذرة واحدة | نفس الملف |

نوع الأرقام: **MEASURED_SMOKE**. نمط التدريب: `partial_finetune_cpu` — 7,681,540 معامل قابل للتدريب من 135,327,748، الحقبة المختارة 9 من 12، 72 خطوة.

### Behavioural checks

| capability | pass rate | known failure |
|---|---:|---|
| تمييز digital_service عن health | — | "الخدمة الإلكترونية واضحة وسريعة" صُنّفت health؛ كلمة "الخدمة" مشتركة بين الفئتين في التدريب، والنظير الإنجليزي صُنّف صحيحًا |

### Limitations and risks
1. 40 صفًا اصطناعيًا لا تكفي لتقدير جودة إنتاجية؛ خطأ واحد على test يساوي 12.5%.
2. validation من 8 أمثلة استُخدم لاختيار الحقبة، فرقم test متفائل بطبيعته.
3. بذرة واحدة بلا تكرار — تباين النتيجة بين البذور غير معروف.

---

## 2. Sentiment classification

### Model details
- Name/version: **غير مدرَّب**
- Base checkpoint: —
- Task: تصنيف المشاعر (positive / negative / neutral)

**الحالة:** عمود `sentiment` موجود في `bayan_day2_classification.csv` لكن **لم يُدرَّب له رأس مستقل**. الدفتر التعليمي يقيس رأس `topic` فقط لإبقاء الـsmoke محدودًا، وينصّ صراحةً على أن نتيجته **لا تُعد دليلًا لرأس sentiment**.

**الخطة:** إعادة استخدام نفس الـsplit المجمّد مع label map مستقلة ورأس تصنيف منفصل، ثم تقييم الرأسين كلٌّ بمقياسه. هذا بند مفتوح موثق، لا ادعاء منجز.

---

## 3. Named Entity Recognition

### Model details
- Name/version: `bayan-ner` / v0.1 (SYSTEMS_SMOKE)
- Base checkpoint: `distilbert/distilbert-base-multilingual-cased`
- Task: استخراج كيانات BIO — SERVICE، LOCATION، DATE، REF_NUM، ORG
- License/source: Apache-2.0، Hugging Face
- Commit SHA: `ba58eff`

### Data and preprocessing
- Dataset ID/version: `bayan_day2_ner.jsonl` — 12 جملة
- Languages: عربية وإنجليزية
- Alignment policy: أول subword من كل كلمة يحمل الـlabel؛ special tokens والأجزاء الفرعية التابعة تأخذ **-100** فيتجاهلها حساب الخسارة.

### Evaluation

| metric/slice | n | result | uncertainty | evidence file |
|---|---:|---:|---|---|
| Strict entity F1 (test) | 4 كيانات | 0.571 | بذرة واحدة | `notebooks/04_ner_and_qa.ipynb` |
| Precision | 4 | 0.667 | — | نفس الدفتر |
| Recall | 4 | 0.500 | — | نفس الدفتر |

القياس على **مستوى الكيان** لا الرمز: حدود الكيان يجب أن تطابق تمامًا وإلا احتُسب خطأ كاملًا. 12 حقبة، 48 خطوة، mean loss = 0.862.

### Limitations and risks
1. 8 جمل تدريب فقط — الرقم وصفي بحت.
2. 4 كيانات في test؛ كل كيان يساوي 25%.
3. لم تُقس النتيجة لكل نوع كيان على حدة.

---

## 4. Extractive QA

### Model details
- Name/version: `bayan-qa` / v0.1 (SYSTEMS_SMOKE)
- Base checkpoint: `distilbert/distilbert-base-multilingual-cased`
- Task: استخراج إجابة من سياق، مع دعم حالة no-answer
- Commit SHA: `ba58eff`

### Data and preprocessing
- Dataset ID/version: `bayan_day2_qa.json` — 10 أمثلة، منها 2 بلا إجابة
- Null policy: أمثلة بلا إجابة تُعيَّن إلى موضع `[CLS]` في start وend. في post-processing يُحسب null_score من logits الموضع صفر ويُقارن بأفضل span صالح؛ إذا تجاوز الفارق العتبة تُعاد `None` مع سبب صريح.

### Evaluation

| metric/slice | n | result | uncertainty | evidence file |
|---|---:|---:|---|---|
| Valid span test | 1 | PASS — استخرج "الرياض" بحدود صحيحة | حتمي | `notebooks/04_ner_and_qa.ipynb` |
| No-answer test | 1 | PASS — أعاد `None`، السبب `no_answer_in_context`، margin = 6.0 | حتمي | نفس الدفتر |
| Training loss | — | 3.645 بعد 3 خطوات | — | نفس الدفتر |

### Behavioural checks

| capability | pass rate | known failure |
|---|---:|---|
| valid span extraction | 1/1 | — |
| no-answer detection | 1/1 | — |

### Limitations and risks
1. **الاختباران يخصان صحة post-processing لا جودة النموذج.** بعد 3 خطوات تدريب، الرأس لم يتعلم شيئًا ذا دلالة.
2. في اختبار الاستدلال غير المقيّم، أخرج النموذج نصًا مقطوعًا ("اغ النقل...") — متوقع تمامًا ومصنّف SMOKE ONLY.
3. لا يوجد EM/F1 مقاس على مجموعة اختبار.

---

## 5. Semantic search — embeddings and re-ranker

### Model details
- Name/version: `bayan-search-index` / manifest v1.0.0
- Embedding model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`، بُعد 384
- Re-ranker: `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`
- Task: استرجاع دلالي ثنائي اللغة مع إعادة ترتيب
- License/source: Apache-2.0 حسب model card على Hugging Face
- Commit SHA: `ba58eff`

### Data and preprocessing
- Dataset ID/version: `bayan_day3_cases.csv` — 24 حالة، sha256 = `7708cbe884a3c268d24ed2cb87ad2f0a8b64b2e6fa6b37a32393b6ae3bd50e5b`
- Languages: عربية (MSA وGulf) وإنجليزية
- Preprocessing profile: `arabic-search/1.0.0` (camel-tools==1.6.0) للعربية، وNFC + توحيد مسافات للإنجليزية — **مطبَّقة على corpus وquery معًا**
- Normalization: L2 على الجهتين — norm_min = 0.99999994، norm_max = 1.0000001
- Index: `IndexFlatIP`، 24 متجهًا × 384

### Evaluation

| metric/slice | n | result | uncertainty | evidence file |
|---|---:|---:|---|---|
| Recall@3 (test، الإجمالي) | 6 | 1.000 | بذرة واحدة | `reports/retrieval_metrics.json` |
| MRR@3 (test، الإجمالي) | 6 | 0.667 | بذرة واحدة | نفس الملف |
| MRR@3 بعد re-ranking | 6 | 0.722 (+0.056) | بذرة واحدة | نفس الملف |
| MRR@3 — language=ar | 3 | 0.500 | SMALL_SLICE | نفس الملف |
| MRR@3 — language=en | 3 | 0.833 | SMALL_SLICE | نفس الملف |
| MRR@3 — monolingual | 4 | 0.750 | SMALL_SLICE | نفس الملف |
| MRR@3 — cross_lingual | 2 | 0.500 | SMALL_SLICE | نفس الملف |
| No-answer accuracy (validation) | 10 | 1.000 | threshold = 0.4592 | نفس الملف |
| No-answer accuracy (test) | 8 | 1.000 | عتبة مجمّدة | نفس الملف |

قرار إعادة الترتيب: `ADOPT_FOR_EXPERIMENT` — مكسب مقيس على عينة صغيرة، مرشح للتجربة لا قرار إنتاج.

### Limitations and risks
1. Recall@3 = 1.0 على corpus من 24 سجلًا متوقع ولا يدل على تعميم.
2. ترتيب العربية أضعف (MRR 0.500) من الإنجليزية (0.833)، وأضعف للاستعلامات عابرة اللغة — لكن كل شريحة من 2–3 أمثلة.
3. **دقة no-answer = 1.000 لا تدل على متانة العتبة:** استعلامات no-answer في العينة بعيدة موضوعيًا عن الـcorpus (وصفة طبخ، حجز ملعب). الحالة الصعبة — استعلام قريب من الموضوع بلا حالة مطابقة — غير ممثلة إطلاقًا.
4. تغيير الـprofile بعد بناء الفهرس يعني أن corpus وquery لم يعودا يتبعان العقد نفسه، فتنهار المطابقة صامتة. الـmanifest يوثّق الحقول التي يستلزم تغييرها إعادة البناء.

---

## Ethical and privacy notes

- كل البيانات المستخدمة **اصطناعية** من حزمة الدورة، ولا تحتوي أسماء حقيقية أو أرقام هوية أو هواتف أو بريدًا شخصيًا أو شكاوى حقيقية.
- أنماط البريد والهاتف التعليمية تُخفى إلى `<EMAIL>` و`<PHONE>` قبل التدريب؛ نسخة العرض `display_text` تُحفظ بلا تعديل للمراجعة.
- وسم `variant` (MSA/Gulf/Arabizi) في البيانات **تعليمي أُنشئ مع العينة، وليس تنبؤ لهجة**. كشف Arabizi heuristic شفاف وليس مصنّفًا مدرَّبًا.
- **لا ادعاء إنتاجي:** كل الأرقام في هذه البطاقة موسومة MEASURED_SMOKE أو COURSE_FIXTURE، وتصف عينات الدورة فقط. المشروع لا يمثل نظامًا حكوميًا حقيقيًا.
- لم تُرفع أوزان نماذج ولا cache ولا مفاتيح API إلى المستودع.

---

## Reproduction

1. افتح الدفاتر بالترتيب من مجلد `notebooks/`: `01` → `07` (و`08` عند اكتماله).
2. استخدم runtime/device: Google Colab، CPU.
3. ثبّت النسخ من `requirements-day*.txt` — أهمها: `transformers==5.15.1`، `tokenizers==0.22.2`، `scikit-learn==1.9.0`، `camel-tools==1.6.0`، `sentence-transformers==6.0.0`، `faiss-cpu==1.15.0`.
4. شغّل **Runtime → Run all** من commit `ba58eff`. البذرة الثابتة في كل الدفاتر: **42**.
5. قارن النتيجة مع الملفات في `reports/`: `arabic_model_comparison.json`، `search_manifest.json`، `retrieval_metrics.json`، `day3_evaluation_fixture.json`.

**ملاحظة على التكرارية:** البيانات والبذرة ثابتتان، فالنتائج قابلة لإعادة الإنتاج على نفس الجهاز. الاختلاف الوحيد المتوقع هو عند توفر GPU — يتغيّر نمط التدريب من `partial_finetune_cpu` إلى `full_finetune` وعدد الحقب من 12 إلى 2، فتختلف الأرقام.
