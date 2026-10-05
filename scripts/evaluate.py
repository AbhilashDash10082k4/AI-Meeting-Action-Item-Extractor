"""
scripts/evaluate.py

Purpose:
    Runs annotated meeting action-item evaluation from the command line.

Working & Flow:
    - Loads dataset/annotated_action_items.json.
    - Uses ExtractionService to produce predictions for each transcript.
    - Prints precision, recall, F1, and TP/FP/FN counts.

Links to:
    - dataset/annotated_action_items.json
    - src/services/extraction_service.py
    - src/evaluation/evaluator.py
"""

import json
from pathlib import Path

from src.evaluation.evaluator import evaluate_dataset
from src.services.extraction_service import ExtractionService


DATASET_PATH = Path(__file__).resolve().parents[1] / "dataset" / "annotated_action_items.json"


def extract_action_items(transcript: str):
    """Runs the production extraction service against one transcript string."""
    service = ExtractionService()
    _, _, items = service.process_transcript_file(
        filename="evaluation.txt",
        content_bytes=transcript.encode("utf-8")
    )
    return items


def main() -> None:
    """Loads the dataset, runs extraction, and prints evaluation metrics."""
    examples = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    metrics = evaluate_dataset(examples, extract_action_items)

    print(f"Precision: {metrics.precision:.4f}")
    print(f"Recall:    {metrics.recall:.4f}")
    print(f"F1:        {metrics.f1:.4f}")
    print(
        f"TP: {metrics.true_positives} | "
        f"FP: {metrics.false_positives} | "
        f"FN: {metrics.false_negatives}"
    )


if __name__ == "__main__":
    main()
