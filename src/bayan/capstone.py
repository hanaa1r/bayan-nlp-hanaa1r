"""Capstone-level bilingual behavioural guardrails.

The Transformer remains the measured primary model.  These narrow overrides
apply only when a text contains an unambiguous domain term and are documented
as a final-system error fix, not as a replacement benchmark.
"""
from __future__ import annotations

import re


_STRONG_TERMS = {
    "transport": (
        "حافلة", "الحافلة", "باص", "الباص", "محطة", "موقف", "مسار الحافلة",
        "bus", "station", "bus stop", "bus route",
    ),
    "permit": (
        "تصريح", "التصريح", "رخصة", "طلب التصريح", "permit", "licence", "license",
    ),
    "health": (
        "عيادة", "العيادة", "موعد صحي", "موعد طبي", "وصفة", "تحليل", "مختبر",
        "clinic", "medical appointment", "prescription", "laboratory", "health record",
    ),
    "digital_service": (
        "رمز التحقق", "تسجيل الدخول", "البوابة", "الخدمة الإلكترونية",
        "verification code", "sign in", "log in", "portal", "online service",
    ),
}


def topic_keyword_override(text: str) -> str | None:
    """Return a topic only for strong, explicit bilingual domain evidence."""

    normalized = re.sub(r"\s+", " ", text.casefold()).strip()
    matches = {
        label
        for label, terms in _STRONG_TERMS.items()
        if any(term.casefold() in normalized for term in terms)
    }
    return next(iter(matches)) if len(matches) == 1 else None
