"""On-demand evaluation against the notebook's sentence-level labels."""

from collections.abc import Sequence
from typing import Any

from codemix_engine import analyze_text
from evaluation_dataset import EVALUATION_DATASET


LABELS = ("English", "Gujarati", "Hindi")


def evaluate_dataset(
    dataset: Sequence[dict[str, Any]] = EVALUATION_DATASET,
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    expected_sets: list[set[str]] = []
    detected_sets: list[set[str]] = []

    for item in dataset:
        result = analyze_text(item["text"])
        expected = set(item["expected_languages"])
        detected = {
            language
            for language, percentage in result["distribution"].items()
            if percentage > 0
        }
        expected_sets.append(expected)
        detected_sets.append(detected)
        records.append(
            {
                "id": item["id"],
                "text": item["text"],
                "expected": ", ".join(
                    language for language in LABELS if language in expected
                ),
                "detected": ", ".join(
                    language for language in LABELS if language in detected
                ),
                "exact_match": expected == detected,
                "cmis": result["cmis"],
                "switches": result["switching_count"],
                "english_percentage": result["distribution"]["English"],
                "gujarati_percentage": result["distribution"]["Gujarati"],
                "hindi_percentage": result["distribution"]["Hindi"],
            }
        )

    if not records:
        return {
            "records": [],
            "exact_match_accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "confusion_matrices": {},
        }

    from sklearn.metrics import (
        f1_score,
        multilabel_confusion_matrix,
        precision_score,
        recall_score,
    )
    from sklearn.preprocessing import MultiLabelBinarizer

    binarizer = MultiLabelBinarizer(classes=LABELS)
    expected_matrix = binarizer.fit_transform(expected_sets)
    detected_matrix = binarizer.transform(detected_sets)
    matrices = multilabel_confusion_matrix(expected_matrix, detected_matrix)

    return {
        "records": records,
        "exact_match_accuracy": sum(
            record["exact_match"] for record in records
        )
        / len(records),
        "precision": precision_score(
            expected_matrix, detected_matrix, average="macro", zero_division=0
        ),
        "recall": recall_score(
            expected_matrix, detected_matrix, average="macro", zero_division=0
        ),
        "f1": f1_score(
            expected_matrix, detected_matrix, average="macro", zero_division=0
        ),
        "confusion_matrices": {
            label: matrix
            for label, matrix in zip(LABELS, matrices)
        },
    }
