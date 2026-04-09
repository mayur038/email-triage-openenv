"""Deterministic grading and reward helpers for email triage benchmark tasks."""

from __future__ import annotations

from typing import Any

from .tasks import EmailTask

FIELD_WEIGHTS = {
    "category": 0.18,
    "priority": 0.12,
    "team": 0.12,
    "status": 0.10,
    "response": 0.20,
    "notes": 0.08,
    "workflow": 0.10,
    "consistency": 0.10,
}
MIN_FINAL_SCORE = 0.01
MAX_FINAL_SCORE = 0.99
MIN_REWARD = 0.01
MAX_REWARD = 0.99


def _reply_score(response: str, task: EmailTask) -> float:
    text = (response or "").strip().lower()
    if not text:
        return 0.0
    words = [word for word in text.split() if word]
    if len(words) < 8:
        return 0.1
    hits = sum(1 for keyword in task.required_reply_keywords if keyword in text)
    score = 0.7 * (hits / len(task.required_reply_keywords))
    if len(words) >= 12:
        score += 0.15
    if "please" in text or "we will" in text:
        score += 0.15
    if task.expected_category == "security_incident" and "pay immediately" in text:
        score = 0.0
    return min(score, 1.0)


def _notes_score(notes: str, task: EmailTask) -> float:
    text = (notes or "").strip().lower()
    if not text:
        return 0.0
    hits = sum(1 for keyword in task.required_note_keywords if keyword in text)
    score = hits / len(task.required_note_keywords)
    if "investigated" in task.required_checks:
        return score
    return min(score, 0.5)


def _consistency_score(ticket: dict[str, Any], task: EmailTask, finalized: bool) -> float:
    score = 0.0
    if ticket.get("category") == task.expected_category and ticket.get("team") == task.expected_team:
        score += 0.4
    if ticket.get("priority") == task.expected_priority:
        score += 0.3
    if ticket.get("status") == "in_progress" and not finalized:
        score += 0.1
    if finalized and ticket.get("status") == "resolved":
        score += 0.2
    return min(score, 1.0)


def grade_ticket(ticket: dict[str, Any], task: EmailTask, completed_checks: set[str], step_count: int, finalized: bool) -> tuple[float, dict[str, float]]:
    workflow_score = 1.0 if all(check in completed_checks for check in task.required_checks) and step_count >= task.min_steps and finalized else 0.0
    breakdown = {
        "category": 1.0 if ticket.get("category") == task.expected_category else 0.0,
        "priority": 1.0 if ticket.get("priority") == task.expected_priority else 0.0,
        "team": 1.0 if ticket.get("team") == task.expected_team else 0.0,
        "status": 1.0 if ticket.get("status") == "resolved" else 0.0,
        "response": _reply_score(ticket.get("response", ""), task),
        "notes": _notes_score(ticket.get("notes", ""), task),
        "workflow": workflow_score,
        "consistency": _consistency_score(ticket, task, finalized),
    }
    raw_score = sum(breakdown[key] * FIELD_WEIGHTS[key] for key in FIELD_WEIGHTS)
    score = min(max(raw_score, MIN_FINAL_SCORE), MAX_FINAL_SCORE)
    return round(score, 4), breakdown


def incremental_reward(previous_score: float, current_score: float, repeated_action: bool, finalize_attempt_blocked: bool, milestone_gain: float) -> float:
    delta = max(current_score - previous_score, 0.0)
    reward = delta + milestone_gain
    if repeated_action and delta == 0.0:
        reward -= 0.05
    if finalize_attempt_blocked:
        reward -= 0.08
    return min(max(round(reward, 4), MIN_REWARD), MAX_REWARD)
