"""Dataset-to-chat conversion helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

INCIDENT_INSTRUCTION = """You are a video incident classifier.

Input: frames at 1 FPS in chronological order. Predict what situation is occurring next.

Output exactly:
class1=<normal|suspicious|abnormal>
class2=<assault|burglary|dump|swoon|vandalism>

No extra text."""


def convert_to_conversation(
    sample: Mapping[str, Any],
    instruction: str = INCIDENT_INSTRUCTION,
    max_images: int = 8,
) -> dict[str, list[dict[str, Any]]]:
    images = list(sample.get("images") or [])[:max_images]
    user_content = [{"type": "text", "text": instruction}]
    user_content.extend({"type": "image", "image": image} for image in images)

    answer = f"class1={sample['class1']}\nclass2={sample['class2']}"
    return {
        "messages": [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": [{"type": "text", "text": answer}]},
        ]
    }


def convert_dataset(
    samples: Iterable[Mapping[str, Any]],
    instruction: str = INCIDENT_INSTRUCTION,
    max_images: int = 8,
) -> list[dict[str, list[dict[str, Any]]]]:
    return [
        convert_to_conversation(sample, instruction=instruction, max_images=max_images)
        for sample in samples
    ]
