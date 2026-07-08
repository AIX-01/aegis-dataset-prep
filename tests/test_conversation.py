from __future__ import annotations

import unittest

from aegis_dataset_prep.conversation import convert_dataset, convert_to_conversation


class ConversationTests(unittest.TestCase):
    def test_convert_to_conversation_caps_images_and_formats_answer(self) -> None:
        sample = {
            "images": list(range(10)),
            "class1": "abnormal",
            "class2": "assault",
        }

        converted = convert_to_conversation(sample, instruction="Classify.", max_images=3)

        self.assertEqual(converted["messages"][0]["role"], "user")
        self.assertEqual(converted["messages"][1]["role"], "assistant")
        self.assertEqual(len(converted["messages"][0]["content"]), 4)
        self.assertEqual(converted["messages"][1]["content"][0]["text"], "class1=abnormal\nclass2=assault")

    def test_convert_dataset_materializes_list(self) -> None:
        samples = [
            {"images": [], "class1": "normal", "class2": "dump"},
            {"images": [], "class1": "suspicious", "class2": "burglary"},
        ]

        converted = convert_dataset(samples)

        self.assertEqual(len(converted), 2)
        self.assertEqual(converted[0]["messages"][1]["content"][0]["text"], "class1=normal\nclass2=dump")


if __name__ == "__main__":
    unittest.main()
