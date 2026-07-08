"""Dataset split과 label count helper."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from typing import Any

from .metrics import CLASS1_LABELS, CLASS2_LABELS

DEFAULT_SPLIT_SEED = 42
DEFAULT_TEST_SIZE = 150


def split_train_test(dataset: Mapping[str, Any], seed: int = DEFAULT_SPLIT_SEED, test_size: int = DEFAULT_TEST_SIZE):
    """legacy train/test split recipe를 재현합니다."""

    from datasets import DatasetDict

    splits = dataset["train"].shuffle(seed=seed).train_test_split(test_size=test_size, seed=seed)
    return DatasetDict({"train": splits["train"], "test": splits["test"]})


def _column_values(records: Any, key: str) -> list[Any]:
    try:
        return list(records[key])
    except (KeyError, TypeError):
        return [row.get(key) for row in records]


def count_labels(records: Any, key: str) -> Counter:
    return Counter(_column_values(records, key))


def label_count_table(
    split_mapping: Mapping[str, Any],
    split_names: Iterable[str] = ("train", "test"),
) -> dict[str, dict[str, dict[str, int]]]:
    table: dict[str, dict[str, dict[str, int]]] = {}
    for split_name in split_names:
        records = split_mapping[split_name]
        table[split_name] = {
            "class1": dict(count_labels(records, "class1")),
            "class2": dict(count_labels(records, "class2")),
        }
    return table


def print_label_counts(
    split_mapping: Mapping[str, Any],
    class1_labels: Iterable[str] = CLASS1_LABELS,
    class2_labels: Iterable[str] = CLASS2_LABELS,
) -> None:
    for split_name, counts in label_count_table(split_mapping).items():
        print(f"===== {split_name} =====")
        print("[class1]")
        for label in class1_labels:
            print(f"  {label}: {counts['class1'].get(label, 0)}")

        print("[class2]")
        for label in class2_labels:
            print(f"  {label}: {counts['class2'].get(label, 0)}")
        print()
