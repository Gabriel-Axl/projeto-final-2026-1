Fly.io quick deploy guide

Prereqs:
- Install `flyctl` (https://fly.io/docs/hands-on/install-flyctl/)
- Have a Fly account and be logged in: `flyctl auth login`

1) Create a new Fly app (replace `my-churn-app`):

```bash
flyctl launch --name my-churn-app --no-deploy --image "" 
```

This will create a `fly.toml`; if you prefer, use the provided `fly.toml.template` as a starting point.

2) (Optional) Create a volume for persistent metrics storage:

```bash
flyctl volumes create metrics_volume --size 1 --region <your-region>
```

3) Set required secrets / env vars on Fly. At minimum configure the API key:

```bash
flyctl secrets set PREDICT_API_KEY="your-secret"
```

If you use an LLM in production, DO NOT set your real LLM key here unless you rotated it.

4) Configure metrics persistence path (optional):

Set `METRICS_PERSIST_PATH` to a writable path inside the volume, for example `/data/metrics_history.jsonl`:

```bash
flyctl secrets set METRICS_PERSIST_PATH="/data/metrics_history.jsonl"
```

5) Deploy:

```bash
flyctl deploy --config fly.toml
```

6) Open the app:

```bash
flyctl open
```

Notes and tips:
- The repository already contains a `Dockerfile` exposing port `8000` and starting `uvicorn`.
- By default the app will persist metrics to whatever path `METRICS_PERSIST_PATH` points to; Fly instances are ephemeral unless you mount a volume.
- Consider disabling the LLM calls (or mocking them) in production to avoid unexpected costs. You can disable by unsetting `GEMINI_API_KEY` or by setting a flag and using a deterministic fallback in `AIAgent`.

If you want, I can:
- generate a filled `fly.toml` that mounts a volume and sets default values, or
- create a GitHub Actions workflow to automatically deploy to Fly when you push to `main`.
