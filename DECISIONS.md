## Day 1 — Tokenizer decision

Checkpoint/tokenizer: google-bert/bert-base-multilingual-cased (مرمّز وأوزان من نفس الـ checkpoint). المرمّز المحلي WordPiece تعليمي فقط.

Corpus slice: 5 جمل اصطناعية ثنائية اللغة من الدفتر (SEED=42)، بعد profile محافظ وإخفاء PII.

Arabic fertility [MEASURED]: 1.75 على الجملة المختلطة (7 رموز / 4 كلمات) بـ mBERT. المرمّز المحلي: 1.36 متوسط على 5 عينات.

English fertility [MEASURED]: 1.00 (5 رموز / 5 كلمات) بـ mBERT.

Truncation rate at max_length=10 [MEASURED]: 0% على 5 جمل قصيرة بالمرمّز المحلي.

Known limitation:
- العينة 5 جمل فقط، توضيحية لا إحصائية.
- fertility المرمّز المحلي غير صالح للمقارنة بين اللغتين لأن قاموسه 27 رمزًا ويعطي [UNK] كثيرة.
- sentencizer يقطع بعد "د." — "راجع د. أحمد." انقسمت لجملتين، وتحتاج استثناء قبل الإنتاج.
- قياس truncation يجب أن يتم قبل enable_truncation، وإلا كل تسلسل يصير بطول max_length والنتيجة 0% حتمًا.

Decision and reason: mBERT مع MAX_LENGTH=12 في هذا الدفتر، وprofile محافظ بلا حذف تشكيل ولا توحيد ألف لأن أيًا منهما لم تثبت فائدته لمهمة محددة بعد. إعادة القياس مطلوبة على corpus حقيقي قبل تثبيت max_length.


## Day 2 — Classification, NER & QA decisions

**Checkpoint والسبب:** distilbert/distilbert-base-multilingual-cased — مشفّر متعدد اللغات يغطي العربية والإنجليزية معًا، وأخف من mBERT الكامل فيناسب CPU. المرمّز والأوزان من نفس الـ checkpoint في المهام الثلاث.

**نوع التنفيذ:** partial_finetune_cpu — جمّدت معظم المشفّر وحدّثت آخر Transformer block مع رأس المهمة، لأن الجهاز CPU ولا GPU متاح. في التصنيف: 7,681,540 معامل قابل للتدريب من 135,327,748.

**Split strategy ودليل عدم التسرب:** split مجمّد في ملف البيانات (train 24 / validation 8 / test 8)، مع group_id يمنع تسرب الحالات المتشابهة. الدالة validate_splits تتحقق أن كل مجموعة تنتمي إلى split واحد فقط وأن الفئات الأربع موجودة في كل split. النتيجة: **group_overlap = 0** على 20 مجموعة.

**Baseline وTransformer metric [MEASURED_SMOKE]:**
- TF-IDF + LinearSVC — validation macro-F1 = 0.6667، test macro-F1 = 0.7333
- Transformer (الحقبة المختارة 9 من 12) — validation macro-F1 = 1.0000، test macro-F1 = 0.8667، accuracy = 0.875
- الفرق على validation: **+0.3333**
- خطأ واحد على test: "الخدمة الإلكترونية واضحة وسريعة" صُنّفت health بدل digital_service. كلمة "الخدمة" مشتركة بين الفئتين في التدريب، والنظير الإنجليزي صُنّف صحيحًا.

**NER alignment policy:** أول subword من كل كلمة يحمل الـ label، وكل ما عداه يأخذ **-100** — أي special tokens ([CLS]/[SEP]/padding) والأجزاء الفرعية التابعة. القياس على **مستوى الكيان** لا على مستوى الرمز: حدود الكيان يجب أن تطابق تمامًا وإلا احتُسب خطأ كاملًا. النتيجة [MEASURED_SMOKE]: entity F1 = 0.5714 (precision 0.667، recall 0.500) على 4 كيانات حقيقية و3 متنبأ بها، بعد 12 حقبة و48 خطوة (mean loss 0.862).

**QA null policy:** أمثلة بلا إجابة تُعيَّن إلى موضع [CLS] في start و end. في post-processing يُحسب null_score من logits الموضع صفر، ويُقارن بأفضل span صالح؛ إذا كان الفارق أكبر من العتبة تُعاد `None` مع سبب صريح. الاختبارات الحتمية: span صالح أعاد "الرياض"، وحالة no-answer أعادت None بالسبب no_answer_in_context وmargin = 6.0. QA loss = 3.645 بعد 3 خطوات فقط.

**ما لا تستطيع العينة الصغيرة إثباته:**
- 40 صف تصنيف و12 جملة NER و10 أمثلة QA لا تكفي لتقدير جودة إنتاجية.
- validation من 8 أمثلة استُخدم لاختيار الحقبة، فرقم test متفائل بطبيعته.
- خطأ واحد على test يساوي 12.5%، فالفروق الصغيرة غير معنوية.
- QA بعد 3 خطوات لم يتعلم شيئًا ذا دلالة؛ الاختبارات الناجحة تخص صحة post-processing لا جودة النموذج.
- لتقدير موثوق نحتاج: بيانات أكبر، عدة بذور مع mean ± range، شرائح لغوية منفصلة (ar مقابل en)، وtest مجمّد لا يُقرأ أثناء الضبط.


## Day 3 — Arabic profile decision

**Profile + version + backend:** profile اسمها `search`، الإصدار 1.0.0، backend هو camel-tools==1.6.0. القواعد: حفظ نسخة العرض، إخفاء PII، تطبيع Unicode بلا compatibility، حذف التطويل والتشكيل، توحيد الألف والألف المقصورة، **مع الإبقاء على التاء المربوطة**.

**ما تغيّر وما حُفظ:** `display_text` تبقى كما وردت ولا يُكتب فوقها؛ `model_text` مشتقة وقابلة لإعادة البناء. مثال: "إِدَارَةُ الحِساب" تبقى كما هي في نسخة العرض وتصير "ادارة الحساب" في نسخة البحث. الأربع golden cases نجحت، و20 صفًا عولجت (Gulf 9، MSA 9، Arabizi 2).

**لماذا لا profile واحدة لكل الـcheckpoints:** كل checkpoint دُرِّب على تمثيل نصي معيّن؛ حذف التشكيل يفيد البحث لكنه قد يمحو تمييزًا تحتاجه مهمة أخرى. والأهم: تغيير الـprofile بعد بناء الفهرس يعني أن corpus وquery لم يعودا يتبعان العقد نفسه، فتنهار المطابقة صامتة.

**Arabizi:** يُمرَّر كما هو في مسار مستقل (`arabizi_passthrough`) ولا يُحوَّل بقواعد تخمينية. الكشف heuristic شفاف (حروف لاتينية + أرقام 2/3/5/6/7/8/9 + صفر حروف عربية)، **وليس مصنّف لهجة مدرَّبًا**. وسم `variant` في البيانات تعليمي أُنشئ مع العينة، لا تنبؤ.

**مقارنة النموذجين [MEASURED_SMOKE]:** على نفس الـsplit والبذرة (42)، بتدريب آخر encoder block + رأس التصنيف، 40 خطوة لكل نموذج:
- distilbert-base-multilingual-cased → Gulf test macro-F1 = 0.0000
- CAMeL-Lab/bert-base-arabic-camelbert-da → Gulf test macro-F1 = 0.6667

**الحدود:** validation من 4 أمثلة وGulf test من 4 أمثلة، بذرة واحدة. كل مثال يساوي 25%، فالفرق وصفي لا إحصائي. النتيجة **متسقة مع التوقع** — نموذج مدرَّب على العربية واللهجات يقرأ نصًا خليجيًا أفضل — لكنها **لا تثبت تفوقًا عامًا**. لتأكيده نحتاج عينة أكبر، عدة بذور، وشرائح مجمدة أوسع.
