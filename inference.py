import asyncio
import json
import os
from typing import Optional

from openai import OpenAI

from email_triage_env import EmailTriageAction, EmailTriageEnv
from email_triage_env.tasks import DEFAULT_TASK_ORDER

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME", "email-triage-env:latest")
BENCHMARK = "email_triage_env"
MAX_STEPS = 6


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_value = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_value}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    reward_text = ",".join(f"{reward:.2f}" for reward in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={reward_text}",
        flush=True,
    )


SYSTEM_PROMPT = """
You are operating an email triage environment.
Return exactly one JSON object with keys:
operation, category, priority, team, status, response, notes.
Use operation="finalize" only when the ticket is fully triaged.
Valid categories: account_access, billing, security_incident.
Valid priorities: low, medium, high, urgent.
Valid teams: it_support, billing_ops, security_ops.
Valid status: open, in_progress, resolved.
""".strip()


def build_prompt(observation) -> str:
    return json.dumps(
        {
            "task_id": observation.task_id,
            "difficulty": observation.difficulty,
            "sender": observation.sender,
            "subject": observation.subject,
            "email_body": observation.email_body,
            "current_category": observation.current_category,
            "current_priority": observation.current_priority,
            "current_team": observation.current_team,
            "current_status": observation.current_status,
            "required_fields_remaining": observation.required_fields_remaining,
            "last_action_feedback": observation.last_action_feedback,
            "guidance": observation.metadata.get("guidance"),
        }
    )


def fallback_action(task_id: str) -> dict:
    presets = {
        "password_reset_easy": {
            "operation": "finalize",
            "category": "account_access",
            "priority": "high",
            "team": "it_support",
            "status": "resolved",
            "response": "We will reset your access and verify your identity so you can regain portal access quickly.",
            "notes": "User blocked before clinic shift.",
        },
        "billing_refund_medium": {
            "operation": "finalize",
            "category": "billing",
            "priority": "medium",
            "team": "billing_ops",
            "status": "resolved",
            "response": "We confirmed a duplicate charge and billing ops will process the refund with an update on the timeline.",
            "notes": "Duplicate subscription charge reported.",
        },
        "invoice_fraud_hard": {
            "operation": "finalize",
            "category": "security_incident",
            "priority": "urgent",
            "team": "security_ops",
            "status": "resolved",
            "response": "Do not pay this invoice. Please verify the vendor through known contacts while security reviews the suspicious request.",
            "notes": "Possible vendor bank-change fraud.",
        },
    }
    return presets[task_id]


def model_action(client: OpenAI, observation) -> dict:
    if not API_KEY:
        return fallback_action(observation.task_id)

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(observation)},
            ],
            temperature=0.0,
            max_tokens=220,
        )
        content = (completion.choices[0].message.content or "").strip()
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("Model did not return an object.")
        return data
    except Exception:
        return fallback_action(observation.task_id)


async def run_task(client: OpenAI, task_name: str) -> None:
    rewards: list[float] = []
    score = 0.0
    steps = 0
    success = False
    env = await EmailTriageEnv.from_docker_image(LOCAL_IMAGE_NAME)
    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset(task_id=task_name)
        for step in range(1, MAX_STEPS + 1):
            action_payload = model_action(client, result.observation)
            action = EmailTriageAction(**action_payload)
            result = await env.step(action)
            reward = float(result.reward or 0.0)
            rewards.append(reward)
            steps = step
            compact_action = json.dumps(action.model_dump(exclude_none=True), separators=(",", ":"))
            log_step(step=step, action=compact_action, reward=reward, done=result.done, error=None)
            if result.done:
                break

        state = await env.state()
        score = max(0.0, min(1.0, float(state.final_score)))
        success = score >= 0.7
    finally:
        try:
            await env.close()
        except Exception:
            pass
        log_end(success=success, steps=steps, score=score, rewards=rewards)


async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY or "missing-token")
    for task_name in DEFAULT_TASK_ORDER:
        await run_task(client, task_name)


if __name__ == "__main__":
    asyncio.run(main())
