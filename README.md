# bayan-nlp-labs
SDAIA Bayan Applied NLP course — labs and evidence
## Day 1 — Text Processing & Tokenisation

- **Profile:** محافظ — NFC، فك HTML، حذف الوسوم، حذف التطويل، توحيد المسافات، إخفاء PII. بدون حذف تشكيل أو توحيد ألف.
- **Token fertility:** المرمّز المحلي 1.36 على 5 عينات. mBERT: العربية 1.75 مقابل الإنجليزية 1.00.
- **Truncation rate:** 0% عند max_length=10. الحد التشغيلي MAX_LENGTH=12.
- **القرار:** google-bert/bert-base-multilingual-cased بمرمّز وأوزان من نفس الـ checkpoint. العينة 5 جمل اصطناعية، توضيحية لا إحصائية.
- **الدفتر:** [notebooks/01_text_processing_tokenization.ipynb](notebooks/01_text_processing_tokenization.ipynb)
- `DAY1_NOTEBOOK1_CORE=PASS`
