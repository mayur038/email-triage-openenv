from __future__ import annotations

from openenv.core.env_server.http_server import create_app

try:
    from email_triage_env.models import EmailTriageAction, EmailTriageObservation
    from server.email_triage_environment import EmailTriageEnvironment
except ImportError:  # pragma: no cover
    from models import EmailTriageAction, EmailTriageObservation
    from email_triage_environment import EmailTriageEnvironment

app = create_app(
    EmailTriageEnvironment,
    EmailTriageAction,
    EmailTriageObservation,
    env_name="email_triage_env",
    max_concurrent_envs=16,
)


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
