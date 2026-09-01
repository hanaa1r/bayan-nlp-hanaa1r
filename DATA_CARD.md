# DATA CARD — Bayan

## Dataset identity

- Name/version: بيانات الدورة الاصطناعية — `bayan-course-sample` v1.0
- Source/creator: أُنشئت للبرنامج التدريبي SDA-AIE-211، أكاديمية سدايا، إعداد المدربة ميعاد المري
- License/permission: بيانات تعليمية اصطناعية مرفقة مع الدورة، مصرَّح باستخدامها داخل المشروع التدريبي
- Data hash or immutable revision: `bayan_day3_cases.csv` sha256 = `7708cbe884a3c268d24ed2cb87ad2f0a8b64b2e6fa6b37a32393b6ae3bd50e5b`؛ workload اليوم الرابع sha256 = `1d1d1c3bef8a582931f6a1c1803671e8fe194fc36ae59cdc4f4feca9fc4d6785`
- Intended educational task: تصنيف موضوع ومشاعر، استخراج كيانات، إجابة استخراجية، وبحث دلالي ثنائي اللغة — لأغراض تعليمية فقط

## Composition

`bayan_day2_classification.csv` — 40 صفًا، 4 فئات × 10:

| Split | Rows | Arabic | English | Groups | Notes |
|---|---:|---:|---:|---:|---|
| train | 24 | 12 | 12 | 12 | الفئات الأربع موجودة |
| validation | 8 | 4 | 4 | 4 | استُخدم لاختيار الحقبة |
| frozen test | 8 | 4 | 4 | 4 | opened once after freeze |

ملفات أخرى: `bayan_day2_ner.jsonl` (12 جملة) · `bayan_day2_qa.json` (10 أمثلة، منها 2 بلا إجابة) · `bayan_day3_arabic.csv` (20 صفًا: Gulf 9، MSA 9، Arabizi 2) · `bayan_day3_cases.csv` (24 حالة: 12 عربية و12 إنجليزية) · `bayan_day3_queries.jsonl` (18 استعلامًا: validation 10 / test 8، منها 6 no-answer) · `bayan_day3_predictions.csv` (36 مثالًا، **COURSE_FIXTURE**)

## Fields and labels

| Field/label | Meaning | Allowed values | Missing-value rule |
|---|---|---|---|
| `example_id` / `record_id` / `case_id` | معرّف فريد | نص فريد (`F-001`، `A-001`، `AR-001`) | إلزامي |
| `group_id` | مفتاح تجميع يمنع تسرب المتشابهات | نص (`DG-A`) | إلزامي في ملف التصنيف |
| `split` | القسم | `train` · `validation` · `test` | إلزامي؛ قيمة غريبة توقف التحقق |
| `language` | اللغة | `ar` · `en` | إلزامي |
| `variant` | وسم تعليمي، **ليس تنبؤ لهجة** | `MSA` · `Gulf` · `Arabizi` · `English` | إلزامي في ملفات اليوم الثالث |
| `channel` | قناة الوصول | `chat` · `web` | اختياري |
| `text` / `summary` | النص المُدخَل | نص حر | إلزامي |
| `resolution` | نص الحل | نص حر | إلزامي في `bayan_day3_cases.csv` |
| `topic` | فئة الموضوع | `digital_service` · `health` · `permit` · `transport` | إلزامي في كل split |
| `sentiment` | فئة المشاعر | `positive` · `negative` · `neutral` | موجود لكن **لم يُدرَّب له رأس** |
| `length_bucket` | تصنيف الطول | `short` · `long` | يُستخدم في الشرائح |
| `tokens` / `ner_tags` | رموز ووسوم BIO | `O` · `B-/I-SERVICE` · `LOCATION` · `DATE` · `REF_NUM` · `ORG` | الطولان يجب أن يتطابقا |
| `answer_text` / `answer_start` | حقول QA | نص؛ `null` لحالات no-answer | **`null` معنى مقصود لا نقص** |
| `relevant_case_ids` | الحالات الصحيحة لكل استعلام | قائمة معرّفات؛ **فارغة** لـno-answer | القائمة الفارغة معنى مقصود |
| `prediction_a` / `prediction_b` | تنبؤات نظامين تعليميين | نفس قيم `topic` | **COURSE_FIXTURE** — لا تُنسب لنموذجي |

## Collection/generation

الأمثلة **مولَّدة اصطناعيًا** من المدربة لأغراض التدريس، ولا تحتوي حالات أو أشخاصًا حقيقيين. كل نص مصاغ ليمثل نمط شكوى أو استفسار خدمي شائعًا دون نسخ محتوى حقيقي. المراجعة من المدربة وأكاديمية سدايا قبل النشر. ما يجعلها اصطناعية: الأسماء والأرقام والمراجع كلها مختلقة (`BAYAN-204`، `test@example.com`)، والتوزيع متوازن بشكل غير طبيعي (10 أمثلة لكل فئة).

## Cleaning and preprocessing

- **Display copy rule:** `display_text` تُحفظ كما وردت **ولا يُكتب فوقها أبدًا**؛ `model_text` مشتقة وقابلة لإعادة البناء من نسخة العرض.
- **PII masking rule:** أنماط البريد والهاتف التعليمية تُستبدل بـ`<EMAIL>` و`<PHONE>` في نسخة النموذج فقط. الإخفاء يغيّر مواضع الأحرف، فأي ربط لاحق يتم عبر نسخة العرض.
- **Arabic profile/version:** `search` v1.0.0، backend = `camel-tools==1.6.0` — NFC بلا compatibility، حذف التطويل والتشكيل، توحيد الألف والألف المقصورة، **مع الإبقاء على التاء المربوطة**. الإنجليزية: NFC + توحيد مسافات فقط. Arabizi: `arabizi_passthrough` بلا تحويل.
- **Deduplication/grouping:** `group_id` يجمع الحالات المتشابهة في مجموعة واحدة تُسند كاملة إلى split واحد.
- **Filtering/exclusions:** لم تُستبعد أمثلة؛ الملف مجمّد كما ورد.

## Split and leakage controls

- **Split method/seed:** split مجمّد مسبقًا في عمود `split` داخل الملف، لا يُعاد توليده. البذرة الثابتة في كل الدفاتر: **42**.
- **Group isolation evidence:** دالة `validate_splits` تتحقق أن كل `group_id` ينتمي إلى split واحد فقط وأن الفئات الأربع موجودة في كل split. النتيجة: **`group_overlap = 0`** على 20 مجموعة — مطبوعة في `notebooks/03_text_classification.ipynb`.
- **Near-duplicate audit:** لم يُنفَّذ فحص تشابه نصي آلي؛ الاعتماد على `group_id` المعطى مسبقًا. **قيد معلوم.**
- **Frozen-test access date and commit:** فُتح مرة واحدة بعد تثبيت الإعدادات، بتاريخ 2026-09-01، commit `ba58eff`. لم تُعدَّل أي إعدادات بعد قراءته.

## Known gaps and risks

- **Dialects/Arabizi:** لهجة خليجية فقط من بين اللهجات العربية. Arabizi ممثَّل بمثالين، يُمرَّر بلا تحويل ولا يُقيَّم — يحتاج transliteration وتقييمًا مستقلين.
- **Class balance:** متوازن بشكل مصطنع (10 لكل فئة). التوزيع الحقيقي غير معروف، والنموذج لم يُختبر على عدم توازن.
- **Synthetic-to-real gap:** النصوص مصاغة بوضوح أعلى من الشكاوى الحقيقية — بلا أخطاء إملائية أو تكرار أو نصوص مبتورة. الأداء على بيانات حقيقية متوقع أن يكون أدنى.
- **Annotation ambiguity:** بعض الأمثلة تحتمل أكثر من فئة — "المرفق انرفض" و"The request is stuck" بلا اسم فئة صريح. صُنّفت `hard_or_ambiguous` في تحليل الأخطاء.
- **Small slices/uncertainty:** معظم شرائح التقييم أقل من 15 مثالًا وتُوسم `SMALL_SLICE`. مجالات الثقة واسعة جدًا (بعضها يمتد نصف المدى الممكن).
- **Misuse/privacy risk:** منخفض — البيانات اصطناعية. الخطر الحقيقي هو **استخدام النتائج كدليل جودة إنتاجية**، وهذا مرفوض صراحة في كل تقارير المشروع.

## Permitted and prohibited use

- **Permitted educational use:** التدريب والتقييم داخل المشروع التدريبي، وتوضيح المفاهيم، وبناء اختبارات ذهبية وسلوكية.
- **Prohibited/high-risk use:** أي استخدام تشغيلي أو حكومي حقيقي؛ أي قرار يمسّ مستفيدًا؛ تقديم هذه البيانات على أنها واقعية؛ نسبة نتائجها إلى أداء إنتاجي؛ استخدام وسم `variant` كتنبؤ لهجة.
- **Human review:** كل تصنيف أخطاء في هذا المشروع يدوي (8 أخطاء مقروءة ومصنّفة). أي قرار مبني على النموذج يحتاج مراجعة بشرية قبل التنفيذ.

## Maintenance

- **Owner/contact through GitHub:** `hanaa1r` عبر issues في `github.com/hanaa1r/bayan-nlp-hanaa1r`. البيانات الأصلية من `almiyead-rgb/bayan-applied-nlp-course`.
- **Change/version policy:** الملفات مجمّدة لهذا التسليم. أي تغيير يستلزم رفع رقم الإصدار وإعادة حساب الـsha256 وإعادة تشغيل الدفاتر المتأثرة.
- **Index/model rebuild triggers:** إعادة بناء فهرس FAISS إلزامية عند تغيّر أي من: نموذج التضمين، بُعد المتجهات، قاعدة التطبيع، profile المعالجة أو إصدارها، أو sha256 للبيانات. هذه الحقول موثقة في `reports/search_manifest.json`، وأي تغيير فيها بلا إعادة بناء يعني أن corpus وquery لم يعودا يتبعان العقد نفسه — فتنهار المطابقة **صامتة**.
