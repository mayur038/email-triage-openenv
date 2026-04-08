# Submission Checklist

- Real-world benchmark selected: email triage for support operations
- `openenv.yaml` present in repo root
- Typed `Action`, `Observation`, and `State` models implemented
- `reset()`, `step()`, and `state` implemented
- 3 deterministic tasks included: easy, medium, hard
- Grader returns score in `0.0` to `1.0`
- Reward provides partial progress and penalties
- Root `inference.py` uses OpenAI client
- `inference.py` reads `API_BASE_URL`, `MODEL_NAME`, `HF_TOKEN`, `LOCAL_IMAGE_NAME`
- Structured stdout logs use `[START]`, `[STEP]`, `[END]`
- `Dockerfile` present in repo root
- `README.md` documents environment, spaces, tasks, setup, and baseline usage
- Verify locally: `docker build .`
- Verify locally: `openenv validate`
- Verify locally: `python inference.py`
- Deploy to Hugging Face Space tagged `openenv`
- Confirm Space returns `200` on `POST /reset`
