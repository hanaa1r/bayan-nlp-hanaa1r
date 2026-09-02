#!/usr/bin/env python3
"""Train independent Bayan topic and sentiment Transformer heads.

Designed for Google Colab.  The script uses train for optimisation, validation
for epoch selection, and opens test once after selection.  It saves both heads,
the Gate-D validation workload, and a machine-readable report.
"""
from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import os
import random
import subprocess
from pathlib import Path


def ensure_dependencies() -> None:
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
    except ImportError:
        subprocess.check_call(
            [
                "python",
                "-m",
                "pip",
                "install",
                "-q",
                "torch",
                "transformers==5.15.1",
                "scikit-learn==1.9.0",
            ]
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=".")
    parser.add_argument(
        "--model-id", default="distilbert/distilbert-base-multilingual-cased"
    )
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    ensure_dependencies()

    import numpy as np
    import torch
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import accuracy_score, f1_score
    from sklearn.pipeline import make_pipeline
    from sklearn.svm import LinearSVC
    from torch.optim import AdamW
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    project = Path(args.project).resolve()
    data_path = project / "data/sample/bayan_day2_classification.csv"
    with data_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    partitions = {
        split: [row for row in rows if row["split"] == split]
        for split in ("train", "validation", "test")
    }
    assert all(partitions.values())
    groups = {split: {row["group_id"] for row in values} for split, values in partitions.items()}
    assert not (groups["train"] & groups["validation"])
    assert not (groups["train"] & groups["test"])
    assert not (groups["validation"] & groups["test"])

    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(args.model_id, use_fast=True)
    artifact_root = project / "artifacts/project-v1"
    artifact_root.mkdir(parents=True, exist_ok=True)
    reports = project / "reports"
    reports.mkdir(exist_ok=True)

    def train_head(target: str) -> dict:
        labels = sorted({row[target] for row in rows})
        label2id = {label: index for index, label in enumerate(labels)}
        id2label = {index: label for label, index in label2id.items()}

        baseline = make_pipeline(
            TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=1),
            LinearSVC(C=0.5, class_weight="balanced", random_state=args.seed),
        )
        baseline.fit(
            [row["text"] for row in partitions["train"]],
            [row[target] for row in partitions["train"]],
        )
        baseline_validation = baseline.predict(
            [row["text"] for row in partitions["validation"]]
        ).tolist()
        tfidf_f1 = f1_score(
            [row[target] for row in partitions["validation"]],
            baseline_validation,
            labels=labels,
            average="macro",
            zero_division=0,
        )

        model = AutoModelForSequenceClassification.from_pretrained(
            args.model_id,
            num_labels=len(labels),
            label2id=label2id,
            id2label=id2label,
        ).to(device)
        if device.type == "cpu":
            for parameter in model.base_model.parameters():
                parameter.requires_grad = False
            for parameter in model.base_model.transformer.layer[-2:].parameters():
                parameter.requires_grad = True
        parameters = [parameter for parameter in model.parameters() if parameter.requires_grad]
        optimizer = AdamW(parameters, lr=2e-5 if device.type == "cuda" else 8e-5)

        def batches(values: list[dict], epoch: int, shuffle: bool) -> list[list[dict]]:
            values = values.copy()
            if shuffle:
                random.Random(args.seed + epoch).shuffle(values)
            return [values[index : index + 4] for index in range(0, len(values), 4)]

        def encode(batch: list[dict], labels_required: bool) -> dict:
            encoded = tokenizer(
                [row["text"] for row in batch],
                padding=True,
                truncation=True,
                max_length=64,
                return_tensors="pt",
            )
            result = {key: value.to(device) for key, value in encoded.items()}
            if labels_required:
                result["labels"] = torch.tensor(
                    [label2id[row[target]] for row in batch], device=device
                )
            return result

        def predict(values: list[dict]) -> list[str]:
            model.eval()
            predictions: list[str] = []
            with torch.inference_mode():
                for batch in batches(values, 0, False):
                    logits = model(**encode(batch, False)).logits
                    predictions.extend(id2label[int(index)] for index in logits.argmax(-1))
            return predictions

        best_f1 = -1.0
        best_epoch = 0
        best_state = None
        history = []
        for epoch in range(1, args.epochs + 1):
            model.train()
            losses = []
            for batch in batches(partitions["train"], epoch, True):
                optimizer.zero_grad(set_to_none=True)
                loss = model(**encode(batch, True)).loss
                if not torch.isfinite(loss):
                    raise RuntimeError(f"non-finite {target} loss")
                loss.backward()
                torch.nn.utils.clip_grad_norm_(parameters, 1.0)
                optimizer.step()
                losses.append(float(loss.detach().cpu()))
            validation_predictions = predict(partitions["validation"])
            validation_f1 = f1_score(
                [row[target] for row in partitions["validation"]],
                validation_predictions,
                labels=labels,
                average="macro",
                zero_division=0,
            )
            history.append(
                {
                    "epoch": epoch,
                    "loss": float(np.mean(losses)),
                    "validation_macro_f1": float(validation_f1),
                }
            )
            print(target, history[-1])
            if validation_f1 > best_f1:
                best_f1 = float(validation_f1)
                best_epoch = epoch
                best_state = copy.deepcopy(model.state_dict())

        assert best_state is not None
        model.load_state_dict(best_state)
        test_predictions = predict(partitions["test"])
        test_truth = [row[target] for row in partitions["test"]]
        test_f1 = f1_score(
            test_truth,
            test_predictions,
            labels=labels,
            average="macro",
            zero_division=0,
        )
        output = artifact_root / target
        model.save_pretrained(output)
        tokenizer.save_pretrained(output)
        return {
            "model_id": args.model_id,
            "artifact_path": output.as_posix(),
            "labels": labels,
            "seed": args.seed,
            "selected_epoch": best_epoch,
            "tfidf_macro_f1": float(tfidf_f1),
            "transformer_macro_f1": float(best_f1),
            "delta_vs_tfidf": float(best_f1 - tfidf_f1),
            "test_macro_f1": float(test_f1),
            "test_accuracy": float(accuracy_score(test_truth, test_predictions)),
            "history": history,
            "test_opened_once_after_selection": True,
        }

    results = {
        "result_label": "MEASURED_PROJECT_ARTIFACT",
        "device": str(device),
        "data": data_path.relative_to(project).as_posix(),
        "split_contract": "group-isolated train/validation/test",
        "topic": train_head("topic"),
        "sentiment": train_head("sentiment"),
    }
    (reports / "classification_metrics.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    topic_validation = artifact_root / "topic_validation.csv"
    with topic_validation.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["example_id", "split", "language", "text", "label"]
        )
        writer.writeheader()
        for row in partitions["validation"]:
            writer.writerow(
                {
                    "example_id": row["example_id"],
                    "split": "validation",
                    "language": row["language"],
                    "text": row["text"],
                    "label": row["topic"],
                }
            )
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print("PROJECT_ARTIFACT_TOPIC", (artifact_root / "topic").as_posix())
    print("PROJECT_ARTIFACT_SENTIMENT", (artifact_root / "sentiment").as_posix())
    print("PROJECT_VALIDATION_CSV", topic_validation.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
