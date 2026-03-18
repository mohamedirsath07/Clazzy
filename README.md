# Clazzy — Fashion Outfit Recommender (V1 Emergency Release)

Clazzy is a lightweight fashion outfit recommender with a React (Vite) frontend and a FastAPI backend. This V1 focuses on guaranteed, deterministic outfit generation to ensure a smooth demo and onboarding experience without heavy ML dependencies.

In this release, the system pairs uploaded items in index order and applies a simple filename-based sanity check (e.g., "shirt" → TOP, "pants" → BOTTOM). No ML model or dimension-based validation blocks the flow.

## Stack
- Frontend: React + Vite + TypeScript, Tailwind
- Backend: FastAPI (Python)
- Optional (disabled in V1): TensorFlow/Keras classifier

## Deterministic Pairing (V1)
- For every two items, the first becomes `TOP`, the second becomes `BOTTOM`.
- A filename heuristic swaps roles if names strongly suggest the opposite (e.g., "pants" detected on the first item and "shirt" on the second).
- No ML model loading. No dimension or metadata validation.

This guarantees that uploading any 2 images yields exactly 1 outfit without errors.

## Repository Layout
- `Fashion-Style/` — Full web app (frontend + backend)
  - `client/` — React app (Vite)
  - `backend/` — FastAPI server
- `export_package/` — Legacy/experimental packaging and scripts
- `test_api.py` — Misc test script
- `Inputs/` — Sample or local inputs (ignored by app logic)

## Prerequisites
- Node.js 18+
- Python 3.10+
- Windows/macOS/Linux

## Quick Start
Open two terminals from the repository root.

1) Backend (FastAPI):
```
cd Fashion-Style/backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```
- API will serve at http://localhost:8001
- V1 runs in "emergency" deterministic mode; no ML model downloads required.

2) Frontend (React/Vite):
```
cd Fashion-Style/client
npm install
npm run dev
```
- App will run at the URL printed by Vite (commonly http://localhost:5173 or http://localhost:5000 depending on config).
- Any warnings related to database connectivity do not affect the outfit demo.

## How It Works (V1)
- Backend: `emergency_recommender.py` performs simple index-based pairing and applies a filename sanity swap.
- Frontend: The client also applies the same deterministic pairing and sanity swap to ensure consistent UX even if the backend is unavailable.

Upload any 2 images and you’ll get a single outfit with positional labels `TOP` and `BOTTOM`.

## API (subset)
- `POST /recommend` — Returns outfits based on provided items and occasion.
  - Response always contains outfits when there are at least 2 items.

## Environment & Secrets
- Place any local secrets in `.env` files (not committed). See `.gitignore` for patterns.
- This V1 does not require ML model files to run.

## Troubleshooting
- Backend stalls on ML imports: V1 avoids TensorFlow imports; ensure you’re running the current `main.py` that uses the emergency recommender.
- Frontend shows DB warnings: Safe to ignore for the outfit demo.
- No outfits: Ensure you have uploaded at least 2 images.

## Next Steps (Post-V1)
- Re-introduce ML classifier behind a feature flag.
- Improve heuristics while preserving non-blocking behavior.
- Add integration tests across the full flow.

---

This V1 is optimized for reliability and speed of demo. Contributions and feedback are welcome!