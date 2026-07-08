from __future__ import annotations

import unittest

from aegis_dataset_prep.metrics import (
    CLASS1_LABELS,
    UNKNOWN_LABEL,
    classification_metrics,
    labels_with_unknown,
    macro_f1,
    parse_c1c2,
    parse_lists,
)


class MetricsTests(unittest.TestCase):
    def test_parse_c1c2_extracts_labels_case_insensitively(self) -> None:
        self.assertEqual(parse_c1c2("CLASS1=Abnormal\nclass2=Assault"), ("abnormal", "assault"))

    def test_parse_c1c2_returns_unknown_for_unparseable_text(self) -> None:
        self.assertEqual(parse_c1c2("not a label"), (UNKNOWN_LABEL, UNKNOWN_LABEL))

    def test_parse_lists_returns_parallel_label_lists(self) -> None:
        class1, class2 = parse_lists(["class1=normal class2=dump", "garbage"])

        self.assertEqual(class1, ["normal", UNKNOWN_LABEL])
        self.assertEqual(class2, ["dump", UNKNOWN_LABEL])

    def test_labels_with_unknown_appends_unknown_when_present(self) -> None:
        labels = labels_with_unknown(["normal"], [UNKNOWN_LABEL], CLASS1_LABELS)

        self.assertEqual(labels[-1], UNKNOWN_LABEL)

    def test_macro_f1_matches_expected_dummy_case(self) -> None:
        true = ["abnormal", "normal", "suspicious"]
        pred = ["abnormal", "normal", UNKNOWN_LABEL]

        self.assertAlmostEqual(macro_f1(true, pred, CLASS1_LABELS), 2 / 3)

    def test_classification_metrics_reports_macro_values(self) -> None:
        true = ["abnormal", "normal", "suspicious"]
        pred = ["abnormal", "normal", UNKNOWN_LABEL]

        metrics = classification_metrics(true, pred, CLASS1_LABELS)

        self.assertAlmostEqual(metrics["accuracy"], 2 / 3)
        self.assertAlmostEqual(metrics["f1_macro"], 2 / 3)


if __name__ == "__main__":
    unittest.main()
