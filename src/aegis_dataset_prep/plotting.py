"""Optional plotting helpers for notebook evaluation."""

from __future__ import annotations

from collections.abc import Sequence


def plot_confusion_matrix(true_labels: Sequence[str], pred_labels: Sequence[str], labels: Sequence[str] | None = None, normalize: bool = True) -> None:
    from sklearn.metrics import confusion_matrix
    import matplotlib.pyplot as plt
    import seaborn as sns

    norm_option = "true" if normalize else None
    matrix = confusion_matrix(true_labels, pred_labels, labels=labels, normalize=norm_option)

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        matrix,
        annot=True,
        fmt=".2f" if normalize else "d",
        cmap="Blues",
        xticklabels=labels if labels else "auto",
        yticklabels=labels if labels else "auto",
    )
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.title("Confusion Matrix" + (" (Normalized)" if normalize else ""))
    plt.tight_layout()
    plt.show()
