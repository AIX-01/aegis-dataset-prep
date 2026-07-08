"""Parsing and metric helpers for incident-classifier outputs."""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

CLASS1_LABELS = ("normal", "suspicious", "abnormal")
CLASS2_LABELS = ("assault", "burglary", "dump", "swoon", "vandalism")
UNKNOWN_LABEL = "unknown"

_CLASS1_PATTERN = re.compile(r"class1\s*=\s*(normal|suspicious|abnormal)", re.IGNORECASE)
_CLASS2_PATTERN = re.compile(r"class2\s*=\s*(assault|burglary|dump|swoon|vandalism)", re.IGNORECASE)


def parse_c1c2(text: str | None) -> tuple[str, str]:
    value = (text or "").lower()
    class1 = _CLASS1_PATTERN.search(value)
    class2 = _CLASS2_PATTERN.search(value)
    return (
        class1.group(1).lower() if class1 else UNKNOWN_LABEL,
        class2.group(1).lower() if class2 else UNKNOWN_LABEL,
    )


def parse_lists(texts: Iterable[str | None]) -> tuple[list[str], list[str]]:
    class1_values: list[str] = []
    class2_values: list[str] = []
    for text in texts:
        class1, class2 = parse_c1c2(text)
        class1_values.append(class1)
        class2_values.append(class2)
    return class1_values, class2_values


def labels_with_unknown(true_labels: Iterable[str], pred_labels: Iterable[str], labels: Sequence[str]) -> list[str]:
    values = set(true_labels) | set(pred_labels)
    result = list(labels)
    if UNKNOWN_LABEL in values and UNKNOWN_LABEL not in result:
        result.append(UNKNOWN_LABEL)
    return result


def accuracy(true_labels: Sequence[str], pred_labels: Sequence[str]) -> float:
    if len(true_labels) != len(pred_labels):
        raise ValueError("true_labels and pred_labels must have the same length.")
    if not true_labels:
        return 0.0
    return sum(true == pred for true, pred in zip(true_labels, pred_labels)) / len(true_labels)


def _precision_recall_f1(true_labels: Sequence[str], pred_labels: Sequence[str], label: str) -> tuple[float, float, float]:
    tp = sum(1 for true, pred in zip(true_labels, pred_labels) if true == label and pred == label)
    fp = sum(1 for true, pred in zip(true_labels, pred_labels) if true != label and pred == label)
    fn = sum(1 for true, pred in zip(true_labels, pred_labels) if true == label and pred != label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def macro_f1(true_labels: Sequence[str], pred_labels: Sequence[str], labels: Sequence[str]) -> float:
    if not labels:
        return 0.0
    return sum(_precision_recall_f1(true_labels, pred_labels, label)[2] for label in labels) / len(labels)


def classification_metrics(
    true_labels: Sequence[str],
    pred_labels: Sequence[str],
    labels: Sequence[str],
) -> dict[str, float]:
    if len(true_labels) != len(pred_labels):
        raise ValueError("true_labels and pred_labels must have the same length.")
    if not labels:
        return {"accuracy": accuracy(true_labels, pred_labels), "precision_macro": 0.0, "recall_macro": 0.0, "f1_macro": 0.0}

    per_label = [_precision_recall_f1(true_labels, pred_labels, label) for label in labels]
    return {
        "accuracy": accuracy(true_labels, pred_labels),
        "precision_macro": sum(row[0] for row in per_label) / len(labels),
        "recall_macro": sum(row[1] for row in per_label) / len(labels),
        "f1_macro": sum(row[2] for row in per_label) / len(labels),
    }
