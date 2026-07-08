from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from aegis_dataset_prep.config import ExperimentConfig, configure_hf_cache


class ExperimentConfigTests(unittest.TestCase):
    def test_loads_supported_values_from_env(self) -> None:
        env = {
            "AEGIS_EXP_NAME": "run",
            "AEGIS_MODEL_REPO": "owner/model",
            "AEGIS_BASE_MODEL": "base/model",
            "AEGIS_DATASET_REPO": "owner/dataset",
            "LORA_RANK": "64",
            "TRAIN_BATCH_SIZE": "16",
        }

        config = ExperimentConfig.from_env(env)

        self.assertEqual(config.exp_name, "run")
        self.assertEqual(config.lora_rank, 64)
        self.assertEqual(config.lora_alpha, 64)
        self.assertEqual(config.batch_size, 16)

    def test_rejects_unsupported_rank(self) -> None:
        with self.assertRaises(ValueError):
            ExperimentConfig.from_env({"LORA_RANK": "12"})

    def test_require_reports_missing_fields(self) -> None:
        config = ExperimentConfig.from_env({})

        with self.assertRaisesRegex(ValueError, "dataset_repo"):
            config.require("dataset_repo")

    def test_configure_hf_cache_sets_all_paths(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            paths = configure_hf_cache("/tmp/hf")

            self.assertEqual(paths["HF_HOME"], "/tmp/hf")
            self.assertEqual(os.environ["HF_HUB_CACHE"], "/tmp/hf/hub")
            self.assertEqual(os.environ["HF_DATASETS_CACHE"], "/tmp/hf/datasets")
            self.assertEqual(os.environ["HF_ASSETS_CACHE"], "/tmp/hf/assets")


if __name__ == "__main__":
    unittest.main()
