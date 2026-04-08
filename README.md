---
title: Email Triage OpenEnv
emoji: 📬
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

`email_triage_env` is a real-world OpenEnv benchmark for customer support operations. The agent reads inbound emails, assigns category/priority/team, drafts a response, and finalizes the ticket. This models a workflow used in IT help desks, billing support, and security escalation queues.

## Why this environment

This benchmark is useful for training and evaluating practical agent skills:

- reading unstructured email text
- converting it into structured operational decisions
- routing work to the correct team
- drafting a safe customer-facing response
- balancing speed with correctness on security-sensitive issues

## Action space

The environment uses a typed `EmailTriageAction` Pydantic model with these fields:

- `operation`: `"triage"` or `"finalize"`
- `category`: one of `account_access`, `billing`, `security_incident`
- `priority`: one of `low`, `medium`, `high`, `urgent`
- `team`: one of `it_support`, `billing_ops`, `security_ops`
- `status`: one of `open`, `in_progress`, `resolved`
- `response`: draft response to the customer
- `notes`: optional internal notes

## Observation space

The environment returns a typed `EmailTriageObservation` containing:

- task metadata: `task_id`, `difficulty`
- customer email fields: `sender`, `subject`, `email_body`
- current ticket state: category, priority, team, status, response, notes
- progress signals: `required_fields_remaining`, `score_breakdown`, `last_action_feedback`
- episode metadata: `done`, `reward`, `max_steps`

## Tasks

Three deterministic tasks are included:

1. `password_reset_easy`
   Difficulty: easy
   Goal: restore account access for a clinician locked out before a shift.
2. `billing_refund_medium`
   Difficulty: medium
   Goal: identify a duplicate subscription charge and route to billing.
3. `invoice_fraud_hard`
   Difficulty: hard
   Goal: detect likely invoice fraud and escalate urgently to security.

## Reward design

Reward is shaped over the full trajectory:

- partial credit for correct category, priority, team, resolution status, and reply quality
- incremental reward when the ticket score improves
- penalty for repeating the same action without progress
- penalty for finalizing too early with a weak score

Each task is graded deterministically on a `0.0` to `1.0` scale.

## Setup

```bash
pip install -e .
python -m server.app
```

## Validation

```bash
openenv validate
uv lock
docker build .
```

## Baseline usage

The repo includes a root-level `inference.py` that:

- uses the OpenAI client
- reads `API_BASE_URL`, `MODEL_NAME`, `HF_TOKEN`, and `LOCAL_IMAGE_NAME`
- runs all three tasks
- emits strict `[START]`, `[STEP]`, and `[END]` logs

Example:

```bash
set HF_TOKEN=your_token
set API_BASE_URL=https://router.huggingface.co/v1
set MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
set LOCAL_IMAGE_NAME=email-triage-env:latest
python inference.py
```

## Baseline scores

Using the included deterministic fallback policy in `inference.py`, the expected scores are:

- `password_reset_easy`: `1.00`
- `billing_refund_medium`: `1.00`
- `invoice_fraud_hard`: `1.00`

If `HF_TOKEN` is set and a live model is used, scores may vary slightly depending on model output quality.
