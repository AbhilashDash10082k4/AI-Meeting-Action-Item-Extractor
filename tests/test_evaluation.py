"""
tests/test_evaluation.py

Purpose:
    Tests deterministic action-item evaluation metrics without calling an external LLM.

Working & Flow:
    - Builds expected and predicted ActionItem objects.
    - Verifies normalized task-owner matching and metric calculations.

Links to:
    - src/evaluation/evaluator.py
    - src/extraction/schemas.py
"""

from src.evaluation.evaluator import evaluate_predictions
from src.extraction.schemas import ActionItem


def make_item(task: str, owner: str | None) -> ActionItem:
    """Creates a minimal ActionItem fixture for evaluation tests."""
    return ActionItem(
        task=task,
        owner=owner,
        deadline=None,
        status="pending",
        confidence=1.0,
        evidence=task,
        source_segment_ids=[]
    )


def test_evaluation_metrics():
    """Calculates precision, recall, and F1 from one match and one miss."""
    expected = [
        make_item("Write tests", "Alice"),
        make_item("Deploy API", "Bob")
    ]
    predicted = [
        make_item("write tests", "Alice"),
        make_item("Deploy frontend", "Charlie")
    ]

    metrics = evaluate_predictions(expected, predicted)

    assert metrics.true_positives == 1
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 1
    assert metrics.precision == 0.5
    assert metrics.recall == 0.5
    assert metrics.f1 == 0.5


def test_evaluation_preserves_missing_owner_as_null():
    """Matches unassigned action items without inventing an owner."""
    expected = [make_item("Publish release notes", None)]
    predicted = [make_item("Publish release notes", None)]

    metrics = evaluate_predictions(expected, predicted)

    assert metrics.true_positives == 1
    assert metrics.false_positives == 0
    assert metrics.false_negatives == 0
    assert metrics.f1 == 1.0
