#!/usr/bin/env python3
"""Strict audit for the numeric Bayan capstone gates.

Unlike the starter structure validator, this script refuses Systems Smoke and
checks the measured project reports.  It is intentionally fail-closed: absent
or malformed evidence is a failure, never an implicit pass.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path.as_posix())
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def nested(data: dict[str, Any], dotted: str) -> Any:
    value: Any = data
    for key in dotted.split("."):
        if not isinstance(value, dict) or key not in value:
            raise KeyError(dotted)
        value = value[key]
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.project).resolve()

    failures: list[str] = []
    passes: list[str] = []

    def require(name: str, condition: bool, detail: str) -> None:
        (passes if condition else failures).append(f"{name}: {detail}")

    try:
        classification = load_json(root / "reports/classification_metrics.json")
        require(
            "T3-topic",
            nested(classification, "topic.transformer_macro_f1")
            - nested(classification, "topic.tfidf_macro_f1") >= 0.08,
            "Transformer improves over TF-IDF by at least 0.08 Macro-F1",
        )
        require(
            "T3-sentiment",
            nested(classification, "sentiment.transformer_macro_f1")
            - nested(classification, "sentiment.tfidf_macro_f1") >= 0.08,
            "independent sentiment head improves by at least 0.08 Macro-F1",
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        failures.append(f"T3 evidence unavailable: {exc}")

    try:
        task = load_json(root / "reports/task_metrics.json")
        require("T4", float(nested(task, "ner.entity_f1")) >= 0.80, "entity F1 >= 0.80")
        require(
            "T5",
            int(nested(task, "qa.no_answer_passed")) >= 17
            and int(nested(task, "qa.no_answer_total")) >= 20,
            "QA no-answer passes >=17/20",
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        failures.append(f"T4/T5 evidence unavailable: {exc}")

    try:
        retrieval = load_json(root / "reports/retrieval_metrics.json")
        require("T7-recall", float(retrieval["recall_at_10"]) >= 0.80, "Recall@10 >= 0.80")
        require("T7-mrr", float(retrieval["mrr_at_10"]) >= 0.70, "MRR@10 >= 0.70")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        failures.append(f"T7 evidence unavailable: {exc}")

    try:
        behaviour = load_json(root / "reports/behavioural_metrics.json")
        require("T8-MFT", float(behaviour["mft_pass_rate"]) >= 0.90, "MFT >= 90%")
        require(
            "T8-invariance",
            float(behaviour["invariance_pass_rate"]) >= 0.95,
            "invariance >= 95%",
        )
        require(
            "T9",
            int(behaviour["manually_reviewed_errors"]) >= 100,
            "at least 100 errors reviewed and classified",
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        failures.append(f"T8/T9 evidence unavailable: {exc}")

    try:
        benchmark = load_json(root / "reports/benchmark_results.json")
        require(
            "T10-artifact",
            benchmark.get("artefact_role") == "PROJECT_ARTIFACT",
            "benchmark uses the trained Bayan project artifact",
        )
        require(
            "T10-http",
            float(nested(benchmark, "http_concurrency_16.p99_ms")) <= 40.0,
            "HTTP p99 <= 40 ms with concurrency=16",
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        failures.append(f"T10 evidence unavailable: {exc}")

    try:
        extension = load_json(root / "reports/extension_metrics.json")
        require(
            "T12",
            extension.get("measured") is True
            and extension.get("independent_from_core") is True
            and extension.get("decision") in {"ADOPT", "REJECT"},
            "independent measured extension has before/after evidence and a decision",
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        failures.append(f"T12 evidence unavailable: {exc}")

    for item in passes:
        print(f"[PASS] {item}")
    for item in failures:
        print(f"[FAIL] {item}")
    print(f"BAYAN_CAPSTONE_GATES={'PASS' if not failures else 'FAIL'}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
