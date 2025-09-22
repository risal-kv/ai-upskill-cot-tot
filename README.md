# ai-upskill-cot-tot

A minimal quick-start to run the backend API and the React frontend.

## Steps

### 1) Clone Repo
```bash
git clone https://github.com/risal-kv/ai-upskill-cot-tot.git
cd ai-upskill-cot-tot/
```

### 2) Start Backend (FastAPI + Uvicorn)
```bash
# Create and activate a virtual environment (Linux/macOS)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env and set your OpenAI API key
cp env_sample .env
# Edit .env and set:
# OPENAI_API_KEY=sk-...

# Start the API server (default CORS allows http://localhost:5173)
uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

Health check (new terminal, optional):
```bash
curl http://localhost:8000/healthz
```

### 3) Start Frontend (Vite + React)
```bash
# If Node.js and npm are not installed (Ubuntu/Debian):
sudo apt update
sudo apt install -y nodejs npm

# From the repo root, go to the UI folder
cd tic_tac_toe_ui

# Install dependencies
npm install

# Configure the API base URL for the frontend
# Create .env in this folder with the following line:
echo "VITE_API_BASE=http://localhost:8000" > .env

# Run the dev server
npm run dev
```

Open the app in your browser at:
```
http://localhost:5173
```

Notes:
- The backend loads environment variables from `.env` automatically.
- If you run the frontend on a different origin, set `CORS_ORIGINS` before starting the backend, e.g.:
```bash
export CORS_ORIGINS="http://localhost:5173"
uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```