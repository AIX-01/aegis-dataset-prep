from __future__ import annotations

import unittest

from aegis_dataset_prep.dataset import label_count_table


class DatasetTests(unittest.TestCase):
    def test_label_count_table_accepts_list_backed_splits(self) -> None:
        splits = {
            "train": [
                {"class1": "normal", "class2": "dump"},
                {"class1": "normal", "class2": "assault"},
            ],
            "test": [
                {"class1": "abnormal", "class2": "vandalism"},
            ],
        }

        table = label_count_table(splits)

        self.assertEqual(table["train"]["class1"]["normal"], 2)
        self.assertEqual(table["train"]["class2"]["dump"], 1)
        self.assertEqual(table["test"]["class1"]["abnormal"], 1)


if __name__ == "__main__":
    unittest.main()
