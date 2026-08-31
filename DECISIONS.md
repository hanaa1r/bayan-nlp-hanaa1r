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
