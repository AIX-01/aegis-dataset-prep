"""환경변수 기반 실험 설정."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

DEFAULT_WANDB_PROJECT = "aegis_cctv_ai_system"
DEFAULT_HF_CACHE_ROOT = "/workspace/.cache/huggingface"
SUPPORTED_LORA_RANKS = (32, 64)
SUPPORTED_BATCH_SIZES = (8, 16)


def _optional_int(env: Mapping[str, str], name: str) -> int | None:
    value = env.get(name)
    if value in (None, ""):
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} 값은 정수여야 합니다.") from exc


@dataclass(frozen=True)
class ExperimentConfig:
    """환경변수에서 읽는 runtime 설정.

    secret이 들어갈 수 있는 값은 notebook의 repr 중심 흐름에 직접 노출하지 않고,
    private runtime에서 login command에만 넘깁니다.
    """

    hf_read_token: str = ""
    hf_write_token: str = ""
    wandb_api_key: str = ""
    exp_name: str = ""
    model_repo_name: str = ""
    model_name: str = ""
    dataset_repo: str = ""
    wandb_entity: str | None = None
    wandb_project: str = DEFAULT_WANDB_PROJECT
    lora_rank: int | None = None
    batch_size: int | None = None
    hf_cache_root: str = DEFAULT_HF_CACHE_ROOT

    @property
    def lora_alpha(self) -> int | None:
        return self.lora_rank

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "ExperimentConfig":
        env = os.environ if env is None else env
        config = cls(
            hf_read_token=env.get("HF_TOKEN_READ", ""),
            hf_write_token=env.get("HF_TOKEN_WRITE", ""),
            wandb_api_key=env.get("WANDB_API_KEY", ""),
            exp_name=env.get("AEGIS_EXP_NAME", ""),
            model_repo_name=env.get("AEGIS_MODEL_REPO", ""),
            model_name=env.get("AEGIS_BASE_MODEL", ""),
            dataset_repo=env.get("AEGIS_DATASET_REPO", ""),
            wandb_entity=env.get("WANDB_ENTITY") or None,
            wandb_project=env.get("WANDB_PROJECT", DEFAULT_WANDB_PROJECT),
            lora_rank=_optional_int(env, "LORA_RANK"),
            batch_size=_optional_int(env, "TRAIN_BATCH_SIZE"),
            hf_cache_root=env.get("AEGIS_HF_CACHE_ROOT", DEFAULT_HF_CACHE_ROOT),
        )
        config.validate_supported_values()
        return config

    def validate_supported_values(self) -> None:
        if self.lora_rank is not None and self.lora_rank not in SUPPORTED_LORA_RANKS:
            allowed = ", ".join(str(v) for v in SUPPORTED_LORA_RANKS)
            raise ValueError(f"LORA_RANK 값은 다음 중 하나여야 합니다: {allowed}.")
        if self.batch_size is not None and self.batch_size not in SUPPORTED_BATCH_SIZES:
            allowed = ", ".join(str(v) for v in SUPPORTED_BATCH_SIZES)
            raise ValueError(f"TRAIN_BATCH_SIZE 값은 다음 중 하나여야 합니다: {allowed}.")

    def require(self, *field_names: str) -> None:
        missing = [name for name in field_names if not getattr(self, name)]
        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"필수 실험 설정이 비어 있습니다: {joined}.")

    def wandb_init_kwargs(self, learning_rate: float = 5e-5) -> dict:
        kwargs = {
            "project": self.wandb_project,
            "name": self.exp_name,
            "config": {
                "learning_rate": learning_rate,
                "lora_rank": self.lora_rank,
                "lora_alpha": self.lora_alpha,
                "batch_size": self.batch_size,
                "dataset": self.dataset_repo,
            },
        }
        if self.wandb_entity:
            kwargs["entity"] = self.wandb_entity
        return kwargs


def configure_hf_cache(root: str = DEFAULT_HF_CACHE_ROOT) -> dict[str, str]:
    """Hugging Face cache 경로를 하나의 runtime-local root 아래로 모읍니다."""

    paths = {
        "HF_HOME": root,
        "HF_HUB_CACHE": os.path.join(root, "hub"),
        "HF_DATASETS_CACHE": os.path.join(root, "datasets"),
        "HF_ASSETS_CACHE": os.path.join(root, "assets"),
    }
    os.environ.update(paths)
    return paths
