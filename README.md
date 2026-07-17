# AI-Powered Intelligent Product Inspection & Manufacturing Decision Support System

Industry 4.0 style quality inspection platform: capture a product photo with a
phone, run it through a multi-module computer-vision pipeline (product /
component / defect detection), evaluate the results against a manufacturing
specification with an explicit **rule engine**, and get a PASS/FAIL decision
with reasons, severity, and suggested corrections — plus a supervisor
verification loop that feeds a continuous-learning dataset.

## Project layout

```
inspection-system/
├── backend/          FastAPI + PostgreSQL + AI inference + rule engine
├── frontend/          React (Vite) dashboard
├── mobile/            React Native (Expo) operator app
├── ai_models/          Training scripts, dataset folders, YOLO configs, weights
└── docker-compose.yml Runs db + backend + frontend together
```

## How the pipeline works

```
Operator Login → Capture Image → Quality Validation (OpenCV) → Preprocessing
→ AI Detection (product / component / defect modules) → Rule Engine
→ PASS/FAIL Decision + Reasons → PDF Report → Store → Supervisor Verification
→ Verified data → Training Dataset → Periodic Retraining → New Model Version
```

The AI never decides PASS/FAIL directly — `backend/app/services/rule_engine.py`
compares raw detections against each product's stored specification (expected
component counts, position tolerances, defect severity mapping) and produces
the final decision. This is what the spec calls the "intelligent rule
validation engine".

## Quickest path: Docker Compose

```bash
cp backend/.env.example backend/.env    # edit SECRET_KEY at minimum
docker compose up --build
```

- Backend API: http://localhost:8000 (docs at `/docs`)
- Frontend dashboard: http://localhost:5173
- Postgres: localhost:5432

Then bootstrap an admin account and a demo product:

```bash
curl -X POST http://localhost:8000/api/auth/bootstrap-admin \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"ChangeMe123!","role":"administrator"}'
```

Or, if running the backend outside Docker, just run `python seed.py` inside
`backend/` — it creates the same admin account plus a demo product
(`DEMO-001`) with a sample specification so you can test an inspection
end-to-end immediately.

Log in to the dashboard with `admin` / `ChangeMe123!` (change this password
immediately in production).

## Running components individually (local dev, no Docker)

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # point DATABASE_URL at a local Postgres
python seed.py          # optional: creates admin + demo product
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Mobile (Expo)
```bash
cd mobile
npm install
# edit src/api/client.js -> API_BASE_URL to your machine's LAN IP
npx expo start
```

## Training your own detection models

The system ships with **stub inference** (empty detections) until real YOLO
weights are present — this keeps the full pipeline runnable end-to-end from
day one for development/demo purposes, without pretending to have accuracy it
doesn't have.

1. Collect images per product, label bounding boxes (Label Studio / CVAT
   recommended) into YOLO format under `ai_models/dataset/<module>/...`.
2. Adjust `ai_models/defect_detection_data.yaml` (and equivalents for
   `product_detection` / `component_detection`) to your classes.
3. Train:
   ```bash
   cd ai_models
   python train.py --module defect_detection --epochs 100
   ```
4. Copy the resulting `best.pt` into `backend/ai_models/weights/` using the
   filename configured in `backend/app/core/config.py`
   (e.g. `defect_detector.pt`), then register it as a `ModelVersion` via the
   `/api/models` endpoints and activate it.
5. Restart the backend — it will pick up the new weights automatically since
   `DetectionModule` loads them from disk at startup.

Retraining is intentionally **manual/periodic**, not automatic: only
supervisor-verified inspections are added to `TrainingDataset`
(`POST /api/inspections/{id}/feedback`), and retraining is triggered
explicitly via `POST /api/models/retrain`.

## Database schema

All tables from the spec are implemented in `backend/app/models/models.py`:
`Users`, `Products`, `Inspection`, `Defects`, `InspectionReport`,
`TrainingDataset`, `RetrainingQueue`, `ModelVersion`, `SupervisorFeedback`.
Use Alembic for schema migrations in production:

```bash
cd backend
alembic revision --autogenerate -m "init"
alembic upgrade head
```

(`Base.metadata.create_all()` in `main.py` auto-creates tables for local
dev/demo convenience — disable that and rely on Alembic once you're managing
a real production database.)

## Security

- JWT auth (`python-jose`), bcrypt password hashing (`passlib`)
- Role-based access control: `operator`, `supervisor`, `administrator`
  (see `require_roles()` in `app/core/security.py`)
- `/api/auth/bootstrap-admin` only works once (while the `users` table is
  empty) — remove or disable it after initial setup in production

## Deployment

A `Dockerfile` is provided for both `backend/` and `frontend/`, and
`docker-compose.yml` wires them up with Postgres. For production:
- put a reverse proxy (nginx/Caddy) in front with TLS
- move `SECRET_KEY`, DB credentials, etc. into real secrets management
- switch `frontend` to `npm run build` + static hosting instead of the dev
  server
- consider object storage (S3-compatible) instead of local `uploads/` for
  captured images/reports at scale

## What's stubbed vs. what's real

| Component | Status |
|---|---|
| Auth, RBAC, DB schema, REST API | Fully implemented |
| Image quality validation + preprocessing (OpenCV) | Fully implemented |
| Rule engine (component counts, tolerances, severity, PASS/FAIL) | Fully implemented |
| PDF report generation | Fully implemented |
| Dashboard (React) — inspections, analytics, reports, model mgmt | Fully implemented |
| Mobile app (Expo) — login, capture, inspect | Functional scaffold |
| YOLO detection modules | Wired up to load real weights; returns empty detections (stub) until you train and drop in weights |
| Periodic retraining | Manual trigger + queue tracking implemented; actual training loop (`train.py`) is a runnable starting point you'll tune per dataset |
| PLC/IoT/barcode/digital-twin/robot integration (spec's "Future Features") | Not implemented — out of scope for this build |
