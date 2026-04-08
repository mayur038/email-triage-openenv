from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field
from openenv.core.env_server.types import Action, Observation, State

Category = Literal["account_access", "billing", "security_incident"]
Priority = Literal["low", "medium", "high", "urgent"]
Team = Literal["it_support", "billing_ops", "security_ops"]
TicketStatus = Literal["open", "in_progress", "resolved"]
Difficulty = Literal["easy", "medium", "hard"]
Operation = Literal["triage", "finalize"]


class EmailTriageAction(Action):
    operation: Operation = "triage"
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    team: Optional[Team] = None
    status: Optional[TicketStatus] = None
    response: Optional[str] = None
    notes: Optional[str] = None


class EmailTriageObservation(Observation):
    task_id: str
    difficulty: Difficulty
    customer_name: str
    sender: str
    subject: str
    email_body: str
    current_category: Optional[Category] = None
    current_priority: Optional[Priority] = None
    current_team: Optional[Team] = None
    current_status: TicketStatus = "open"
    current_response: str = ""
    agent_notes: str = ""
    required_fields_remaining: list[str] = Field(default_factory=list)
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    last_action_feedback: str = ""
    max_steps: int = 6


class EmailTriageState(State):
    task_id: Optional[str] = None
    difficulty: Optional[Difficulty] = None
    final_score: float = 0.0
    last_reward: float = 0.0
    finalized: bool = False
    current_category: Optional[Category] = None
    current_priority: Optional[Priority] = None
    current_team: Optional[Team] = None
    current_status: TicketStatus = "open"
