from __future__ import annotations

from typing import Any

from .tasks import EmailTask

FIELD_WEIGHTS = {
    "category": 0.25,
    "priority": 0.20,
    "team": 0.20,
    "status": 0.10,
    "response": 0.25,
}


def _reply_score(response: str, task: EmailTask) -> float:
    text = (response or "").strip().lower()
    if not text:
        return 0.0
    hits = sum(1 for keyword in task.required_reply_keywords if keyword in text)
    return hits / len(task.required_reply_keywords)


def grade_ticket(ticket: dict[str, Any], task: EmailTask) -> tuple[float, dict[str, float]]:
    breakdown = {
        "category": 1.0 if ticket.get("category") == task.expected_category else 0.0,
        "priority": 1.0 if ticket.get("priority") == task.expected_priority else 0.0,
        "team": 1.0 if ticket.get("team") == task.expected_team else 0.0,
        "status": 1.0 if ticket.get("status") == "resolved" else 0.0,
        "response": _reply_score(ticket.get("response", ""), task),
    }
    score = sum(breakdown[key] * FIELD_WEIGHTS[key] for key in FIELD_WEIGHTS)
    return round(score, 4), breakdown


def incremental_reward(previous_score: float, current_score: float, repeated_action: bool, finalized: bool) -> float:
    delta = max(current_score - previous_score, 0.0)
    reward = delta
    if repeated_action and delta == 0.0:
        reward -= 0.05
    if finalized and current_score < 0.7:
        reward -= 0.10
    return max(0.0, min(1.0, round(reward, 4)))
