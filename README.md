---
title: Email Triage OpenEnv
emoji: "📬"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
tags:
  - openenv
  - docker
  - benchmark
---

# Email Triage OpenEnv

`email_triage_env` is a real-world OpenEnv environment for customer support email handling.  
The agent reads an incoming email, understands the problem, assigns the right category and priority, routes it to the correct team, writes a response, and closes the ticket.

This is based on a task that people really do in support teams, billing teams, and security teams every day.

## What We Built

We built a complete OpenEnv benchmark for **email triage**, a common business workflow.

In this environment, an AI agent must:

- read a customer email
- understand what kind of issue it is
- decide how urgent it is
- send it to the correct team
- draft a helpful and safe reply
- finalize the ticket correctly

The project includes:

- a full OpenEnv-compatible environment
- typed `Action`, `Observation`, and `State` models
- `reset()`, `step()`, and `state()` support
- `openenv.yaml`
- 3 graded tasks with increasing difficulty
- shaped rewards with partial progress signals
- a reproducible baseline `inference.py`
- Docker deployment support
- Hugging Face Space deployment support

## Why This Problem Matters

Email triage is a useful real-world task because it tests whether an agent can turn messy text into correct operational decisions.

This environment measures practical skills such as:

- reading unstructured text
- understanding business context
- routing work correctly
- handling urgency
- writing clear customer replies
- taking extra care in security-sensitive cases

## Why This Submission Is Strong

This project is designed to match the hackathon goals closely:

- **Real-world utility**: email triage is a real workflow used by support, billing, and security teams
- **Task quality**: the tasks move from easy to medium to hard and each one has a clear goal
- **Deterministic grading**: each task has fixed expected outcomes and scores in the range `0.0` to `1.0`
- **Reward shaping**: the agent gets partial credit for progress instead of only getting a final binary result
- **Deployment-ready**: the project includes `openenv.yaml`, `Dockerfile`, `uv.lock`, and a root-level `inference.py`
- **Practical benchmark value**: the environment checks classification, prioritization, routing, and safe response writing in one benchmark

## Environment Overview

Each episode gives the agent one incoming email.  
The agent must update the ticket fields and eventually finalize the case.

The environment tracks:

- the original email
- the current ticket state
- which fields are still missing
- how much progress the agent has made
- whether the ticket is ready to close

## Action Space

The environment uses a typed `EmailTriageAction` model with these fields:

- `operation`: `"triage"` or `"finalize"`
- `category`: `account_access`, `billing`, or `security_incident`
- `priority`: `low`, `medium`, `high`, or `urgent`
- `team`: `it_support`, `billing_ops`, or `security_ops`
- `status`: `open`, `in_progress`, or `resolved`
- `response`: customer-facing reply
- `notes`: optional internal note

## Observation Space

The environment returns a typed `EmailTriageObservation` containing:

- `task_id`
- `difficulty`
- `customer_name`
- `sender`
- `subject`
- `email_body`
- current category, priority, team, and status
- current response and notes
- `required_fields_remaining`
- `score_breakdown`
- `last_action_feedback`
- `reward`
- `done`
- `max_steps`

## Tasks

The benchmark includes 3 deterministic tasks:

1. `password_reset_easy`
   An urgent account access problem. The agent should route it to IT support and help the user regain access quickly.

2. `billing_refund_medium`
   A duplicate charge case. The agent should identify it as a billing issue, route it to billing, and explain the refund process.

3. `invoice_fraud_hard`
   A suspicious vendor payment request. The agent should recognize it as a security incident, mark it urgent, and tell the customer not to pay before verification.

These tasks move from easy to hard and test both classification and safe decision-making.

Business impact of the tasks:

- easy: blocked operational access before a shift
- medium: refund and customer trust risk
- hard: potential financial fraud and security escalation

## Reward Design

The reward is not just a final pass/fail score.  
It gives useful signals during the full episode.

The agent receives reward for:

- choosing the correct category
- assigning the correct priority
- selecting the correct team
- resolving the case properly
- writing a reply that includes the important points

The agent is penalized for:

- repeating the same non-helpful action
- finalizing too early with a weak solution

Final task scores are always in the range `0.0` to `1.0`.

## Grading

Each task has a deterministic grader.

The grader checks:

- category correctness
- priority correctness
- routing correctness
- resolution status
- response quality using required keywords

This makes scoring reproducible and easy to validate.

## Project Structure

```text
.
|-- email_triage_env/
|   |-- client.py
|   |-- grader.py
|   |-- models.py
|   `-- tasks.py
|-- server/
|   |-- app.py
|   `-- email_triage_environment.py
|-- inference.py
|-- openenv.yaml
|-- Dockerfile
|-- pyproject.toml
`-- README.md
```

## Setup

```bash
pip install -e .
python -m server.app
```

The server runs on port `8000`.

## Validation

```bash
openenv validate
uv lock
docker build .
```

## Baseline Inference

The root-level `inference.py` script:

- uses the OpenAI client
- reads credentials from environment variables
- runs all 3 tasks
- prints logs in the required `[START]`, `[STEP]`, and `[END]` format

Required environment variables:

- `HF_TOKEN`
- `API_BASE_URL`
- `MODEL_NAME`
- `LOCAL_IMAGE_NAME`

Example:

```bash
set HF_TOKEN=your_token
set API_BASE_URL=https://router.huggingface.co/v1
set MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
set LOCAL_IMAGE_NAME=email-triage-env:latest
python inference.py
```

## Baseline Scores

Using the included fallback policy in `inference.py`, the expected scores are:

- `password_reset_easy`: `1.00`
- `billing_refund_medium`: `1.00`
- `invoice_fraud_hard`: `1.00`

If a live hosted model is used, the score may vary slightly depending on model quality.

## Deployment

This project is ready for Hugging Face Spaces with `sdk: docker`.

Live Space:

- [https://huggingface.co/spaces/mayurgohil/email-triage-openenv](https://huggingface.co/spaces/mayurgohil/email-triage-openenv)
- [https://mayurgohil-email-triage-openenv.hf.space](https://mayurgohil-email-triage-openenv.hf.space)

## Summary

This project delivers a complete OpenEnv environment for a real support workflow.

It is designed to evaluate whether an AI agent can:

- understand customer problems
- make structured support decisions
- route tickets safely
- communicate clearly
- handle harder security cases correctly

That makes it a practical benchmark for training and evaluating real-world AI agents.
