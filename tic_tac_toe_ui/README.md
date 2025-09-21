# Tic Tac Toe UI (React + Vite)

This is a React UI for a Tic Tac Toe game that integrates with an AI backend. The backend supports two reasoning modes:

- CoT (Chain-of-Thought): returns a chosen move and a textual reasoning string
- ToT (Tree-of-Thought): returns a chosen move, summary reasoning, and a tree structure with thoughts/reasons per node

## Getting Started

1. Install Node.js and npm (if not installed):

- Linux (Debian/Ubuntu):
```bash
sudo apt update
sudo apt install -y nodejs npm
```
- macOS (Homebrew):
```bash
brew install node
```
- Windows: install from the official site: `https://nodejs.org`

Verify:
```bash
node -v
npm -v
```

2. Install project dependencies:

```bash
npm install
```

3. Configure environment variables (backend URL):

Create a `.env` file in this folder with:
```bash
# If your backend runs on a different host/port, set it here
VITE_API_BASE=http://localhost:8000
```
- If omitted, the UI defaults to `http://localhost:8000` (see `src/lib/api.ts`).
- You can also point to a deployed backend URL.

(Optional) Use the built-in mock AI for demos without a backend:
```bash
# .env
VITE_USE_MOCK_AI=true
```

4. Run the dev server:

```bash
npm run dev
```

5. Build for production:

```bash
npm run build
```

## Backend API Contract

Endpoint:

- `POST {VITE_API_BASE}/api/v1/move`

Request JSON body:

```json
{
  "board": ["X", null, "O", null, "X", null, null, "O", null],
  "player": "O",
  "mode": "tot"
}
```

- `board`: length-9 array with values `"X" | "O" | null`
- `player`: the AI's mark to play next (`"X"` or `"O"`)
- `mode`: `"cot"` or `"tot"`

Responses:

CoT:

```json
{
  "mode": "cot",
  "move": 6,
  "reasoning": "I block the fork and set up a win next move."
}
```

ToT:

```json
{
  "mode": "tot",
  "move": 2,
  "reasoning": "Explored candidate moves and selected the highest scoring branch.",
  "tree": {
    "thought": "Consider center control",
    "reason": "Center maximizes options",
    "score": 0.7,
    "children": [
      {
        "thought": "If opponent blocks here",
        "reason": "Maintain double threat",
        "children": []
      }
    ]
  }
}
```

Notes:
- `move` is 0..8 index into the board.
- `tree` is recursive. Each node has `thought`, `reason`, optional `score`, and optional `children`.

## UI Features

- Interactive 3x3 board; human selects `X` or `O`
- Mode switch between CoT and ToT
- Automatically requests AI move when it's AI's turn
- Displays CoT reasoning text or ToT tree view with collapsible nodes

## Customization

- Styles in `src/index.css`
- API client in `src/lib/api.ts`
- Game logic in `src/lib/game.ts`
- Components under `src/components/`
