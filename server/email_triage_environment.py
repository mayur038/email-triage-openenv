from __future__ import annotations

import uuid
from typing import Optional

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import EnvironmentMetadata

try:
    from email_triage_env.grader import grade_ticket, incremental_reward
    from email_triage_env.models import EmailTriageAction, EmailTriageObservation, EmailTriageState
    from email_triage_env.tasks import DEFAULT_TASK_ORDER, TASKS, EmailTask
except ImportError:  # pragma: no cover
    from grader import grade_ticket, incremental_reward
    from models import EmailTriageAction, EmailTriageObservation, EmailTriageState
    from tasks import DEFAULT_TASK_ORDER, TASKS, EmailTask


class EmailTriageEnvironment(Environment[EmailTriageAction, EmailTriageObservation, EmailTriageState]):
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self) -> None:
        super().__init__()
        self.max_steps = 6
        self._task_order = DEFAULT_TASK_ORDER
        self._task_index = 0
        self._episode_id: Optional[str] = None
        self._step_count = 0
        self._finalized = False
        self._last_reward = 0.0
        self._last_score = 0.0
        self._current_task: Optional[EmailTask] = None
        self._ticket = self._empty_ticket()

    def _empty_ticket(self) -> dict:
        return {
            "category": None,
            "priority": None,
            "team": None,
            "status": "open",
            "response": "",
            "notes": "",
        }

    def _select_task(self, task_id: Optional[str]) -> EmailTask:
        if task_id:
            return TASKS[task_id]
        task = TASKS[self._task_order[self._task_index % len(self._task_order)]]
        self._task_index += 1
        return task

    def _required_fields_remaining(self) -> list[str]:
        missing = []
        if not self._ticket["category"]:
            missing.append("category")
        if not self._ticket["priority"]:
            missing.append("priority")
        if not self._ticket["team"]:
            missing.append("team")
        if self._ticket["status"] != "resolved":
            missing.append("status")
        if not self._ticket["response"].strip():
            missing.append("response")
        return missing

    def _feedback(self, breakdown: dict[str, float]) -> str:
        complete = [key for key, value in breakdown.items() if value >= 1.0]
        partial = [key for key, value in breakdown.items() if 0.0 < value < 1.0]
        remaining = [key for key, value in breakdown.items() if value == 0.0]
        parts = []
        if complete:
            parts.append(f"Correct: {', '.join(complete)}.")
        if partial:
            parts.append(f"Partial: {', '.join(partial)}.")
        if remaining:
            parts.append(f"Still needs work: {', '.join(remaining)}.")
        return " ".join(parts) or "No progress yet."

    def _build_observation(self, score_breakdown: dict[str, float], feedback: str, done: bool) -> EmailTriageObservation:
        assert self._current_task is not None
        return EmailTriageObservation(
            task_id=self._current_task.task_id,
            difficulty=self._current_task.difficulty,
            customer_name=self._current_task.customer_name,
            sender=self._current_task.sender,
            subject=self._current_task.subject,
            email_body=self._current_task.body,
            current_category=self._ticket["category"],
            current_priority=self._ticket["priority"],
            current_team=self._ticket["team"],
            current_status=self._ticket["status"],
            current_response=self._ticket["response"],
            agent_notes=self._ticket["notes"],
            required_fields_remaining=self._required_fields_remaining(),
            score_breakdown=score_breakdown,
            last_action_feedback=feedback,
            max_steps=self.max_steps,
            reward=self._last_reward,
            done=done,
            metadata={
                "guidance": self._current_task.guidance,
                "business_impact": self._current_task.business_impact,
                "success_criteria": self._current_task.success_criteria,
            },
        )

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_id: Optional[str] = None,
        **kwargs,
    ) -> EmailTriageObservation:
        del seed, kwargs
        self._episode_id = episode_id or str(uuid.uuid4())
        self._step_count = 0
        self._finalized = False
        self._last_reward = 0.0
        self._last_score = 0.0
        self._current_task = self._select_task(task_id)
        self._ticket = self._empty_ticket()
        return self._build_observation(
            score_breakdown={"category": 0.0, "priority": 0.0, "team": 0.0, "status": 0.0, "response": 0.0},
            feedback="Review the email and begin triage.",
            done=False,
        )

    def step(
        self,
        action: EmailTriageAction,
        timeout_s: Optional[float] = None,
        **kwargs,
    ) -> EmailTriageObservation:
        del timeout_s, kwargs
        if self._current_task is None:
            raise RuntimeError("Environment must be reset before stepping.")

        self._step_count += 1
        previous_ticket = dict(self._ticket)

        if action.category is not None:
            self._ticket["category"] = action.category
        if action.priority is not None:
            self._ticket["priority"] = action.priority
        if action.team is not None:
            self._ticket["team"] = action.team
        if action.status is not None:
            self._ticket["status"] = action.status
        if action.response is not None:
            self._ticket["response"] = action.response
        if action.notes is not None:
            self._ticket["notes"] = action.notes
        if action.operation == "finalize":
            self._finalized = True
            if self._ticket["status"] != "resolved":
                self._ticket["status"] = "resolved"

        score, breakdown = grade_ticket(self._ticket, self._current_task)
        repeated_action = previous_ticket == self._ticket
        self._last_reward = incremental_reward(self._last_score, score, repeated_action, self._finalized)
        self._last_score = score

        done = self._finalized or self._step_count >= self.max_steps
        if done and not self._finalized and self._ticket["status"] != "resolved":
            self._ticket["status"] = "in_progress"

        feedback = self._feedback(breakdown)
        return self._build_observation(score_breakdown=breakdown, feedback=feedback, done=done)

    @property
    def state(self) -> EmailTriageState:
        return EmailTriageState(
            episode_id=self._episode_id,
            step_count=self._step_count,
            task_id=self._current_task.task_id if self._current_task else None,
            difficulty=self._current_task.difficulty if self._current_task else None,
            final_score=self._last_score,
            last_reward=self._last_reward,
            finalized=self._finalized,
            current_category=self._ticket["category"],
            current_priority=self._ticket["priority"],
            current_team=self._ticket["team"],
            current_status=self._ticket["status"],
        )

    def get_metadata(self) -> EnvironmentMetadata:
        return EnvironmentMetadata(
            name="email_triage_env",
            description="A real-world customer support triage benchmark for account, billing, and security emails.",
            version="0.1.0",
            author="Hackathon submission",
        )
