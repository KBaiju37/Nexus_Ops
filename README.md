# NexusOps Lite

NexusOps Lite is a local-first deployment, monitoring, and incident diagnosis platform that simulates application deployments, tracks incidents, and surfaces ML-based troubleshooting guidance.

## Overview

This project demonstrates a practical DevOps workflow with:

- FastAPI backend
- SQLAlchemy + SQLite persistence
- React + TypeScript + Vite frontend
- deterministic deployment simulator
- incident creation and status tracking
- supervised ML log analysis with TF-IDF + Logistic Regression
- Docker Compose runtime
- GitHub Actions CI validation
- Terraform validation configuration

## Folder structure

```text
NexusOps-Lite/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── infrastructure/
│   └── terraform/
├── .github/workflows/ci.yml
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── ...
```

## Local installation

On Windows PowerShell:

```powershell
cd C:\Users\baijunath karvir\Desktop\Nexus_Ops\NexusOps-Lite
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

## Backend startup

```powershell
cd C:\Users\baijunath karvir\Desktop\Nexus_Ops\NexusOps-Lite
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger documentation is available at http://localhost:8000/docs.

## Frontend startup

```powershell
cd C:\Users\baijunath karvir\Desktop\Nexus_Ops\NexusOps-Lite
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Then visit http://localhost:5173.

## Docker Compose startup

```powershell
cd C:\Users\baijunath karvir\Desktop\Nexus_Ops\NexusOps-Lite
docker compose up --build
```

## Testing

```powershell
cd C:\Users\baijunath karvir\Desktop\Nexus_Ops\NexusOps-Lite
.\.venv\Scripts\Activate.ps1
cd backend
pytest
```

## ML classification workflow

The project uses a supervised text-classification model based on a locally generated dataset. It combines TF-IDF vectorization and a logistic regression classifier from scikit-learn. The model is trained on log examples from categories such as database failures, memory issues, network timeouts, authentication errors, and dependency build failures.

This is not an autonomous root-cause engine or a production-grade AI agent. It is a lightweight local classifier designed to support troubleshooting recommendations.

## GitHub Actions

The workflow under `.github/workflows/ci.yml` installs backend dependencies, runs Pytest, installs frontend modules, and validates the frontend build.

## Terraform validation

```powershell
cd C:\Users\baijunath karvir\Desktop\Nexus_Ops\NexusOps-Lite\ninfrastructure\terraform
terraform fmt
terraform validate
```

## Known limitations

- The deployment simulator is intentionally deterministic for testability.
- The ML model is trained on a small synthetic dataset rather than production telemetry.
- This is a local-first demonstration platform, not a multi-tenant cloud deployment system.

## Future improvements

- Add real deployment execution workers
- Add persistent auth and RBAC
- Add richer metrics and charts
- Add richer incident workflow automation

# Nexus_Ops
