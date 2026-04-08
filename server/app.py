from __future__ import annotations

from openenv.core.env_server.http_server import create_app

try:
    from email_triage_env.models import EmailTriageAction, EmailTriageObservation
    from email_triage_env.tasks import DEFAULT_TASK_ORDER
    from server.email_triage_environment import EmailTriageEnvironment
except ImportError:  # pragma: no cover
    from models import EmailTriageAction, EmailTriageObservation
    from tasks import DEFAULT_TASK_ORDER
    from email_triage_environment import EmailTriageEnvironment

app = create_app(
    EmailTriageEnvironment,
    EmailTriageAction,
    EmailTriageObservation,
    env_name="email_triage_env",
    max_concurrent_envs=16,
)


@app.get("/")
def root() -> dict:
    return {
        "name": "email_triage_env",
        "status": "running",
        "message": "Email Triage OpenEnv is live. Use POST /reset and POST /step to interact with the environment.",
        "tasks": DEFAULT_TASK_ORDER,
    }


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "environment": "email_triage_env",
        "tasks": DEFAULT_TASK_ORDER,
    }


@app.get("/about")
def about() -> dict:
    return {
        "name": "email_triage_env",
        "description": "Agents triage support emails by classifying, prioritizing, routing, and replying.",
        "tasks": DEFAULT_TASK_ORDER,
        "api_examples": {
            "reset": "POST /reset",
            "step": "POST /step",
            "state": "GET /state",
        },
    }


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
