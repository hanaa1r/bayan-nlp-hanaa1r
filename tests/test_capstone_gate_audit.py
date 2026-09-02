from pathlib import Path


def test_strict_gate_audit_exists_and_refuses_smoke_wording():
    text = Path("scripts/capstone_gate_audit.py").read_text(encoding="utf-8")
    assert "PROJECT_ARTIFACT" in text
    assert "SYSTEMS_SMOKE" not in text
    assert "manually_reviewed_errors" in text
    assert "http_concurrency_16.p99_ms" in text
