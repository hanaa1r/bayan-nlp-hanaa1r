# DATA CARD — Bayan

## Dataset identity

- Name/version: بيانات الدورة الاصطناعية — `bayan-course-sample` من مستودع `almiyead-rgb/bayan-applied-nlp-course`
- Source/creator: أُنشئت للبرنامج التدريبي SDA-AIE-211، أكاديمية سدايا، إعداد المدربة ميعاد المري
- License/permission: بيانات تعليمية اصطناعية مرفقة مع الدورة، مصرَّح باستخدامها داخل المشروع التدريبي
- Data hash or immutable revision: `bayan_day3_cases.csv` sha256 = `7708cbe884a3c268d24ed2cb87ad2f0a8b64b2e6fa6b37a32393b6ae3bd50e5b`؛ workload اليوم الرابع sha256 = `1d1d1c3bef8a582931f6a1c1803671e8fe194fc36ae59cdc4f4feca9fc4d6785`؛ باقي الملفات مثبتة في `data/sample/` بالمستودع
- Intended educational task: تصنيف موضوع ومشاعر، استخراج كيانات، إجابة استخراجية، وبحث دلالي ثنائي اللغة — لأغراض تعليمية فقط

## Composition

### `bayan_day2_classification.csv` — التصنيف

| Split | Rows | Arabic | English | Groups | Notes |
|---|---:|---:|---:|---:|---|
| train | 24 | ~12 | ~12 | 12 | 4 فئات موضوع متوازنة |
| validation | 8 | ~4 | ~4 | 4 | استُخدم لاختيار الحقبة |
| frozen test | 8 | ~4 | ~4 | 4 | opened once after freeze |

الإجمالي 40 صفًا، 4 فئات × 10. **group_overlap = 0** على 20 مجموعة — لا مجموعة تظهر في أكثر من split.

### ملفات أخرى

| الملف | الحجم | ملاحظات |
|---|---:|---|
| `bayan_day1_sample.csv` | — | عينات اليوم الأول |
| `bayan_day2_ner.jsonl` | 12 جملة | train 8 / validation 2 / test 2، وسوم BIO |
| `bayan_day2_qa.json` | 10 أمثلة | منها 2 بلا إجابة (no-answer) |
| `bayan_day3_arabic.csv` | 20 صفًا | Gulf 9، MSA 9، Arabizi 2 |
| `bayan_day3_cases.csv` | 24 حالة | corpus البحث الدلالي، 12 عربية و12 إنجليزية |
| `bayan_day3_queries.jsonl` | 18 استعلامًا | validation 10 / test 8؛ منها 6 no-answer |
| `bayan_day3_predictions.csv` | 36 مثالًا | **COURSE_FIXTURE** — تنبؤات تعليمية، ليست مخرجات نموذجي |

## Fields and labels

| Field/label | Meaning | Allowed values | Missing-value rule |
|---|---|---|---|
| `example_id` / `record_id` / `case_id` | معرّف فريد للصف | نص فريد (مثل `F-001`، `A-001`، `AR-001`) | إلزامي — الصف مرفوض بدونه |
| `group_id` | مفتاح تجميع يمنع تسرب الحالات المتشابهة بين الـsplits | نص (مثل `DG-A`) | إلزامي في ملف التصنيف |
| `split` | القسم | `train` · `validation` · `test` | إلزامي؛ قيمة غير معروفة تُوقف التحقق |
| `language` | لغة النص | `ar` · `en` | إلزامي |
| `variant` | وسم **تعليمي** أُنشئ مع العينة، **وليس تنبؤ لهجة** | `MSA` · `Gulf` · `Arabizi` · `English` | إلزامي في ملفات اليوم الثالث |
| `channel` | قناة الوصول | `chat` · `web` | اختياري |
| `text` / `summary` | النص المُدخَل | نص حر | إلزامي |
| `resolution` | نص الحل في حالات البحث | نص حر | إلزامي في `bayan_day3_cases.csv` |
| `topic` | فئة الموضوع | `digital_service` · `health` · `permit` · `transport` | إلزامي — كل فئة موجودة في كل split |
| `sentiment` | فئة المشاعر | `positive` · `negative` · `neutral` | موجود في البيانات لكن **لم يُدرَّب له رأس** — بند مفتوح موثق |
| `length_bucket` | تصنيف الطول | `short` · `long` | يُستخدم في شرائح التقييم |
| `tokens` / `ner_tags` | رموز الجملة ووسومها | وسوم BIO: `O` · `B-/I-SERVICE` · `B-/I-LOCATION` · `B-/I-DATE` · `B-/I-REF_NUM` · `B-/I-ORG` | الطولان يجب أن يتطابقا وإلا رُفض الصف |
| `question` / `context` / `answer_text` / `answer_start` | حقول QA | نص؛ `answer_text = null` و`answer_start = null` لحالات no-answer | القيمة `null` **معنى مقصود** لا نقص بيانات |
| `relevant_case_ids` | معرّفات الحالات الصحيحة لكل استعلام | قائمة معرّفات؛ **قائمة فارغة** لاستعلامات no-answer | القائمة الفارغة معنى مقصود |
| `prediction_a` / `prediction_b` | تنبؤات نظامين تعليميين | نفس قيم `topic` | **COURSE_FIXTURE** — لا تُنسب لأي نموذج دربته |

## Preprocessing contract

- **نسختان لا نسخة واحدة:** `display_text` تُحفظ كما وردت ولا يُكتب فوقها؛ `model_text` مشتقة وقابلة لإعادة البناء.
- **Profile العربية:** `search` v1.0.0، backend = `camel-tools==1.6.0` — NFC بلا compatibility، حذف التطويل والتشكيل، توحيد الألف والألف المقصورة، **مع الإبقاء على التاء المربوطة**.
- **الإنجليزية:** NFC + توحيد المسافات فقط.
- **Arabizi:** يُمرَّر كما هو (`arabizi_passthrough`) بلا تحويل بقواعد تخمينية.
- corpus وquery يمران بنفس الدالة — أي اختلاف يعني مقارنة فضاءين مختلفين.

## Privacy and ethics

- **كل البيانات اصطناعية.** لا أسماء حقيقية، لا أرقام هوية، لا هواتف، لا بريد شخصي، لا شكاوى حقيقية، لا أسرار مؤسسية.
- أنماط البريد والهاتف التعليمية تُخفى إلى `<EMAIL>` و`<PHONE>` في نسخة النموذج؛ نسخة العرض تبقى للمراجعة.
- وسم `variant` تعليمي، ولا يُقدَّم كتنبؤ لهجة. كشف Arabizi heuristic شفاف، وليس مصنّفًا مدرَّبًا.
- المشروع **لا يمثل نظامًا حكوميًا حقيقيًا** ولا يستخدم بيانات حساسة.

## Limitations

1. **الحجم:** 40 صف تصنيف، 12 جملة NER، 10 أمثلة QA، 24 حالة بحث، 36 مثال تقييم. لا شيء منها يكفي لتقدير جودة إنتاجية.
2. **التمثيل:** لهجة خليجية فقط من بين اللهجات العربية؛ أربع فئات موضوع فقط؛ Arabizi ممثَّل بمثالين ولا يُقيَّم.
3. **الشرائح الصغيرة:** معظم شرائح التقييم أقل من 15 مثالًا وتُوسم `SMALL_SLICE`؛ مجالات الثقة واسعة جدًا.
4. **حالات no-answer سهلة:** استعلامات no-answer بعيدة موضوعيًا عن الـcorpus (وصفة طبخ، حجز ملعب). الحالة الصعبة — استعلام قريب من الموضوع بلا حالة مطابقة — **غير ممثلة إطلاقًا**.
5. **`bayan_day3_predictions.csv` تنبؤات تعليمية**، لا مخرجات نموذج ولا benchmark.
6. **عمود `sentiment` غير مستغَل:** موجود في البيانات لكن لم يُدرَّب له رأس مستقل — بند مفتوح موثق في `MODEL_CARD.md`.

## Provenance

كل الملفات محفوظة في `data/sample/` داخل المستودع، ومصدرها الأصلي:
`https://github.com/almiyead-rgb/bayan-applied-nlp-course/tree/main/data/sample`

الدفاتر تنزّلها من الرابط وقت التشغيل (`data_source = github_course_file`)، وتستخدم نسخة مدمجة احتياطية عند تعذر الاتصال (`embedded_fallback`).
## Collection/generation

FILL_ME: كيف أنشئت أو جُمعت الأمثلة؟ ما الذي يجعلها اصطناعية/عامة؟ من راجعها؟

## Cleaning and preprocessing

- Display copy rule: FILL_ME
- PII masking rule: FILL_ME
- Arabic profile/version: FILL_ME
- Deduplication/grouping: FILL_ME
- Filtering/exclusions: FILL_ME

## Split and leakage controls

- Split method/seed: FILL_ME
- Group isolation evidence: FILL_ME
- Near-duplicate audit: FILL_ME
- Frozen-test access date and commit: FILL_ME

## Known gaps and risks

- Dialects/Arabizi: FILL_ME
- Class balance: FILL_ME
- Synthetic-to-real gap: FILL_ME
- Annotation ambiguity: FILL_ME
- Small slices/uncertainty: FILL_ME
- Misuse/privacy risk: FILL_ME

## Permitted and prohibited use

- Permitted educational use: FILL_ME
- Prohibited/high-risk use: FILL_ME
- Human review: FILL_ME

## Maintenance

- Owner/contact through GitHub: FILL_ME
- Change/version policy: FILL_ME
- Index/model rebuild triggers: FILL_ME
