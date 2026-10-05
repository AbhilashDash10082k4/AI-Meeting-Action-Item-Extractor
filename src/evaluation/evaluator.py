"""
src/evaluation/evaluator.py

Purpose:
    Evaluates action-item extraction against an annotated meeting dataset.

Working & Flow:
    - normalize_item creates a stable comparison representation for an ActionItem.
    - evaluate_predictions computes true positives, false positives, false negatives,
      precision, recall, and F1.
    - evaluate_dataset evaluates annotated examples using a supplied extraction callable.

Links to:
    - src/extraction/schemas.py
    - dataset/annotated_action_items.json
    - scripts/evaluate.py
    - tests/test_evaluation.py
"""

from collections.abc import Callable
from dataclasses import dataclass

from src.extraction.schemas import ActionItem


@dataclass(frozen=True)
class EvaluationMetrics:
    """Contains aggregate extraction accuracy counts and metrics."""

    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float


def normalize_item(item: ActionItem) -> tuple[str, str | None]:
    """Creates a normalized task-owner key used for deterministic matching."""
    task = " ".join(item.task.lower().split())
    owner = item.owner.lower().strip() if item.owner else None
    return task, owner


def evaluate_predictions(
    expected: list[ActionItem],
    predicted: list[ActionItem]
) -> EvaluationMetrics:
    """Computes exact normalized task-owner precision, recall, and F1."""
    expected_keys = {normalize_item(item) for item in expected}
    predicted_keys = {normalize_item(item) for item in predicted}

    true_positives = len(expected_keys & predicted_keys)
    false_positives = len(predicted_keys - expected_keys)
    false_negatives = len(expected_keys - predicted_keys)

    precision = (
        true_positives / (true_positives + false_positives)
        if true_positives + false_positives
        else 0.0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if true_positives + false_negatives
        else 0.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return EvaluationMetrics(
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        precision=precision,
        recall=recall,
        f1=f1
    )


def evaluate_dataset(
    examples: list[dict],
    extract: Callable[[str], list[ActionItem]]
) -> EvaluationMetrics:
    """Evaluates all annotated transcript examples using the supplied extractor."""
    expected_items: list[ActionItem] = []
    predicted_items: list[ActionItem] = []

    for example in examples:
        expected_items.extend(
            ActionItem.model_validate(item)
            for item in example["action_items"]
        )
        predicted_items.extend(extract(example["transcript"]))

    return evaluate_predictions(expected_items, predicted_items)
