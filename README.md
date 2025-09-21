# ai-upskill-cot-tot

A small modular project demonstrating CoT/ToT-style reasoning on Tic-Tac-Toe across two checkpoints.

### Prerequisites
- Python 3.11 recommended (3.10+ should work)
- An OpenAI API key

Verify your Python version:
```bash
python3 --version
```

### 1) Create and activate a virtual environment
Linux / macOS:
```bash
cd ai-upskill-cot-tot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Windows (PowerShell):
```powershell
cd ai-upskill-cot-tot
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Configure environment variables (.env)
Create a `.env` at the repo root (same folder as `requirements.txt`). A starter is provided:
```bash
cp env_sample .env
```
Edit `.env` and set your key:
```
OPENAI_API_KEY=sk-...
```

Notes:
- `checkpoint_2` auto-loads `.env` via `python-dotenv`.
- `checkpoint_3` reads environment variables from the process. The easiest cross-platform way to ensure `.env` is loaded at runtime is to use the `python-dotenv` runner shown below.

### 4) Run the apps
Activate your virtual environment first (step 1) in every new shell.

- Run checkpoint 2 (simple CoT tic-tac-toe):
```bash
python -m checkpoint_2.main
```

- Run checkpoint 3 (tree-of-thoughts with search):
```bash
# This uses python-dotenv to load .env into the environment for the process
python -m dotenv run -- python -m checkpoint_3.main --beam 2 --depth 2
```
You can adjust search parameters, for example:
```bash
python -m dotenv run -- python -m checkpoint_3.main --beam 3 --depth 3
```

### Start the API server (FastAPI + Uvicorn)
The UI calls a REST API defined in `api/server.py`.

- Start the server (hot reload):
```bash
uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

- Optional: set allowed CORS origins (comma-separated). Defaults to `http://localhost:3000,http://localhost:5173`.
```bash
export CORS_ORIGINS="http://localhost:5173"
uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

- Health check:
```bash
curl http://localhost:8000/healthz
```

- Move endpoint (example body):
```bash
curl -X POST http://localhost:8000/api/v1/move \
  -H 'Content-Type: application/json' \
  -d '{
    "mode": "cot",
    "player": "O",
    "board": [null,null,null,null,null,null,null,null,null]
  }'
```

### Troubleshooting
- Missing API key: Ensure `OPENAI_API_KEY` is set. For checkpoint 3, prefer running via:
```bash
python -m dotenv run -- python -m checkpoint_3.main
```
- Virtualenv not active: If `python` points to a system interpreter, re-run `source .venv/bin/activate` (Linux/macOS) or `\.\.venv\Scripts\Activate.ps1` (Windows PowerShell).
- Network/429 errors: Reduce request rate or retry; ensure the key has access to the specified model in `checkpoint_3/config.py` (default `gpt-4o-mini`).

### Project layout (key files)
- `checkpoint_2/`: CoT-style game loop
  - `main.py`: entry point (loads `.env` automatically)
- `checkpoint_3/`: ToT-style search and visualization toggles
  - `main.py`: entry point (pass `--beam` and `--depth`)
  - `config.py`: toggles and defaults (reads `OPENAI_API_KEY` from env)

### Deactivate the virtual environment
```bash
deactivate
```