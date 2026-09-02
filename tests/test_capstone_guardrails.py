import pytest

from bayan.capstone import topic_keyword_override


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("وين موقع موقف الباص في الحي؟", "transport"),
        ("The bus route is missing from the map", "transport"),
        ("تأخر إصدار التصريح المطلوب", "permit"),
        ("The permit request is under review", "permit"),
        ("نتيجة التحليل لم تظهر", "health"),
        ("My clinic appointment was cancelled", "health"),
        ("لم يصل رمز التحقق", "digital_service"),
        ("I cannot sign in to the portal", "digital_service"),
    ],
)
def test_strong_bilingual_topic_terms(text, expected):
    assert topic_keyword_override(text) == expected


def test_ambiguous_or_unknown_text_defers_to_model():
    assert topic_keyword_override("The request is stuck") is None
    assert topic_keyword_override("الخدمة غير واضحة") is None
