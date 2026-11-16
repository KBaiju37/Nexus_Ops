from pathlib import Path

base = Path(r'C:\Users\baijunath karvir\Desktop\Nexus_Ops\NexusOps-Lite')

files = {
    'backend/requirements.txt': r'''fastapi==0.115.0
uvicorn[standard]==0.30.6
SQLAlchemy==2.0.36
Pydantic==2.10.6
pydantic-settings==2.6.1
pytest==8.3.3
httpx==0.27.2
scikit-learn==1.5.2
joblib==1.4.2
python-dotenv==1.0.1
''',
    'backend/Dockerfile': r'''FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
''',
    'backend/app/__init__.py': '',
    'backend/app/config.py': r'''from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NexusOps Lite"
    app_env: str = "development"
    database_url: str = "sqlite:///./nexusops.db"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    log_level: str = "INFO"
    ml_threshold: float = 0.55

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
''',
    'backend/app/database.py': r'''from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
''',
    'backend/app/main.py': r'''from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routes.analytics import router as analytics_router
from app.routes.applications import router as applications_router
from app.routes.deployments import router as deployments_router
from app.routes.incidents import router as incidents_router
from app.routes.monitoring import router as monitoring_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Local-first deployment monitoring and incident diagnosis platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications_router, prefix="/applications", tags=["applications"])
app.include_router(deployments_router, prefix="/deployments", tags=["deployments"])
app.include_router(incidents_router, prefix="/incidents", tags=["incidents"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(monitoring_router, tags=["monitoring"])


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}


@app.get("/")
def root():
    return {"name": settings.app_name, "status": "running"}
''',
    'backend/app/models/__init__.py': '',
    'backend/app/models/application.py': r'''from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    repository_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    environment: Mapped[str] = mapped_column(String(50), default="dev")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
''',
    'backend/app/models/deployment.py': r'''from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    scenario: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="Pending")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    logs: Mapped[str] = mapped_column(Text, default="")
    failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    incident_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
''',
    'backend/app/models/incident.py': r'''from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    deployment_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default="Medium")
    error_logs: Mapped[str] = mapped_column(Text, default="")
    root_cause_category: Mapped[str] = mapped_column(String(100), default="Unknown")
    diagnosis: Mapped[str] = mapped_column(Text, default="")
    recommended_resolution: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default="Open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    ml_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ml_confidence: Mapped[float | None] = mapped_column(nullable=True)
''',
    'backend/app/schemas/__init__.py': '',
    'backend/app/schemas/application.py': r'''from datetime import datetime

from pydantic import BaseModel, Field


class ApplicationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(default="", max_length=1000)
    repository_url: str | None = Field(default=None, max_length=500)
    environment: str = Field(default="dev", max_length=50)


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationRead(ApplicationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
''',
    'backend/app/schemas/deployment.py': r'''from datetime import datetime

from pydantic import BaseModel, Field


class DeploymentCreate(BaseModel):
    application_id: int
    version: str = Field(..., min_length=1, max_length=80)
    scenario: str = Field(..., min_length=2, max_length=40)


class DeploymentRead(BaseModel):
    id: int
    application_id: int
    version: str
    scenario: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    logs: str
    failure_reason: str | None = None
    incident_id: int | None = None

    class Config:
        from_attributes = True
''',
    'backend/app/schemas/incident.py': r'''from datetime import datetime

from pydantic import BaseModel, Field


class IncidentPatch(BaseModel):
    status: str | None = Field(default=None, max_length=30)
    severity: str | None = Field(default=None, max_length=20)
    diagnosis: str | None = Field(default=None)
    recommended_resolution: str | None = Field(default=None)


class IncidentRead(BaseModel):
    id: int
    deployment_id: int
    severity: str
    error_logs: str
    root_cause_category: str
    diagnosis: str
    recommended_resolution: str
    status: str
    created_at: datetime
    ml_category: str | None = None
    ml_confidence: float | None = None

    class Config:
        from_attributes = True
''',
    'backend/app/services/deployment_engine.py': r'''from datetime import datetime, timedelta

SCENARIO_MAP = {
    "successful": {
        "status": "Succeeded",
        "logs": [
            "INFO: Validating application configuration.",
            "INFO: Installing dependencies for release.",
            "INFO: Building application bundle.",
            "INFO: Starting application process.",
            "INFO: Health check passed on port 8080.",
            "INFO: Deployment completed successfully.",
        ],
        "failure_reason": None,
    },
    "build_failure": {
        "status": "Failed",
        "logs": [
            "ERROR: Build step failed during dependency compilation.",
            "ERROR: ModuleNotFoundError: settings not available.",
            "ERROR: npm install exited with code 1.",
            "ERROR: Deployment aborted before runtime validation.",
        ],
        "failure_reason": "Build failure: dependency compilation failed before application startup.",
    },
    "dependency_installation_failure": {
        "status": "Failed",
        "logs": [
            "ERROR: Failed to install Python requirements.",
            "ERROR: Could not resolve package versions from lock file.",
            "ERROR: Installation aborted due to package conflict.",
        ],
        "failure_reason": "Dependency installation failure: required packages could not be resolved.",
    },
    "application_startup_failure": {
        "status": "Failed",
        "logs": [
            "ERROR: Application process exited immediately after startup.",
            "ERROR: Missing environment variable API_URL.",
            "ERROR: Gunicorn process terminated with exit code 1.",
        ],
        "failure_reason": "Application startup failure: runtime process crashed on boot.",
    },
    "health_check_failure": {
        "status": "Failed",
        "logs": [
            "INFO: Application started.",
            "ERROR: Health endpoint returned HTTP 500.",
            "ERROR: Readiness probe failed for /health.",
            "ERROR: Deployment marked unhealthy after startup.",
        ],
        "failure_reason": "Health-check failure: application reported unhealthy readiness after start.",
    },
}


def simulate_deployment(version: str, scenario: str) -> dict:
    scenario_key = scenario.strip().lower().replace(" ", "_")
    config = SCENARIO_MAP[scenario_key]
    started_at = datetime.utcnow()
    completed_at = started_at + timedelta(minutes=2)
    logs = "\n".join(config["logs"])
    return {
        "version": version,
        "scenario": scenario_key,
        "status": config["status"],
        "started_at": started_at,
        "completed_at": completed_at,
        "logs": logs,
        "failure_reason": config["failure_reason"],
    }
''',
    'backend/app/services/recommendation_engine.py': r'''from app.ml.train_model import FALLBACK_RULES


def build_recommendation(category: str, logs: str) -> str:
    normalized = category.strip().lower()
    if normalized in FALLBACK_RULES:
        return FALLBACK_RULES[normalized]["recommendation"]
    if "database" in logs.lower():
        return "Validate database connectivity, credentials, host reachability, and connection pooling configuration."
    if "memory" in logs.lower() or "oom" in logs.lower():
        return "Review memory limit settings, increase container headroom, and inspect heap allocation patterns."
    if "timeout" in logs.lower() or "network" in logs.lower():
        return "Check upstream network policies, DNS resolution, and latency or firewall paths to dependent services."
    return "Inspect recent release changes, confirm runtime configuration, and validate service health before retrying the deployment."
''',
    'backend/app/services/incident_manager.py': r'''from app.models.incident import Incident
from app.services.log_classifier import analyze_logs
from app.services.recommendation_engine import build_recommendation


SEVERITY_BY_CATEGORY = {
    "Database Connection Failure": "High",
    "Memory/Resource Problem": "High",
    "Network Timeout": "Medium",
    "Application Exception": "High",
    "Authentication Failure": "High",
    "Dependency/Build Failure": "Critical",
    "Unknown": "Medium",
}


def create_incident_from_deployment(deployment, db) -> Incident:
    analysis = analyze_logs(deployment.logs)
    category = analysis["category"]
    logs = deployment.logs or ""
    recommendation = build_recommendation(category, logs)
    incident = Incident(
        deployment_id=deployment.id,
        severity=SEVERITY_BY_CATEGORY.get(category, "Medium"),
        error_logs=logs,
        root_cause_category=category,
        diagnosis=analysis["diagnosis"],
        recommended_resolution=recommendation,
        status="Open",
        ml_category=analysis["category"],
        ml_confidence=analysis["confidence"],
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident
''',
    'backend/app/ml/training_data.py': r'''LOG_TRAINING_DATA = {
    "Database Connection Failure": [
        "ERROR: Unable to connect to PostgreSQL database. Connection timed out.",
        "FATAL: Database connection refused while connecting to the primary instance.",
        "SQLAlchemy OperationalError: could not connect to server: Connection refused.",
        "ERROR: database host unreachable after migration rollout.",
        "Database connection error: password authentication failed for app_user.",
    ],
    "Memory/Resource Problem": [
        "OutOfMemoryError: Java heap space exhausted during deployment.",
        "ERROR: container memory limit reached while starting background workers.",
        "Killed process due to high memory pressure from the application container.",
        "Resource temporarily unavailable while allocating memory for cache.",
        "The service ran out of memory and restarted unexpectedly.",
    ],
    "Network Timeout": [
        "Timeout connecting to upstream API service after 30 seconds.",
        "ERROR: network timeout while fetching metadata from edge gateway.",
        "Socket timeout reading response from third-party service.",
        "HTTP request failed due to connectivity issue and timeout.",
        "Gateway response timed out while waiting for backend service.",
    ],
    "Application Exception": [
        "Traceback: ValueError: invalid response payload from parser.",
        "Unhandled exception in worker thread: KeyError on session state.",
        "ERROR: application crash caused by unexpected None value.",
        "Exception in api route: TypeError: unsupported operand for object.",
        "Runtime exception thrown while processing upload request.",
    ],
    "Authentication Failure": [
        "401 Unauthorized token expired while authenticating service account.",
        "Authentication failed for user session after JWT refresh.",
        "Permission denied: access token invalid for the requested service.",
        "ERROR: SSO callback rejected due to invalid credentials.",
        "Authentication server returned 403 forbidden for the service principal.",
    ],
    "Dependency/Build Failure": [
        "ERROR: Build failed because the package manager could not install dependency.",
        "ModuleNotFoundError: missing package while compiling the release artifact.",
        "Dependency resolution failed during build step before startup.",
        "Failed to install project dependencies and aborted release pipeline.",
        "Compilation error: dependency version mismatch in requirements file.",
    ],
}

FALLBACK_RULES = {
    "database connection failure": {
        "category": "Database Connection Failure",
        "severity": "High",
        "diagnosis": "Database connection could not be established.",
        "recommendation": "Verify database host, port, credentials, and service availability.",
    },
    "memory/resource problem": {
        "category": "Memory/Resource Problem",
        "severity": "High",
        "diagnosis": "Application memory or resource limits were exceeded.",
        "recommendation": "Increase memory limits, inspect memory usage, and trim unnecessary cache allocations.",
    },
    "network timeout": {
        "category": "Network Timeout",
        "severity": "Medium",
        "diagnosis": "The application timed out while contacting an upstream dependency.",
        "recommendation": "Review networking policy, DNS resolution, and timeout settings for upstream services.",
    },
    "application exception": {
        "category": "Application Exception",
        "severity": "High",
        "diagnosis": "An application-level exception caused the release to fail.",
        "recommendation": "Inspect the traceback, validate runtime inputs, and confirm the application is resilient to bad payloads.",
    },
    "authentication failure": {
        "category": "Authentication Failure",
        "severity": "High",
        "diagnosis": "The application could not authenticate to a required service.",
        "recommendation": "Validate tokens, credentials, and identity configuration before retrying the deployment.",
    },
    "dependency/build failure": {
        "category": "Dependency/Build Failure",
        "severity": "Critical",
        "diagnosis": "Dependency resolution or build tooling failed before the application could start.",
        "recommendation": "Check dependency versions, lock files, and build environment settings before rerunning the pipeline.",
    },
}
''',
    'backend/app/ml/train_model.py': r'''import os
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.ml.training_data import FALLBACK_RULES, LOG_TRAINING_DATA

MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "log_classifier.joblib"


def build_model_pipeline():
    texts = []
    labels = []
    for category, examples in LOG_TRAINING_DATA.items():
        for example in examples:
            texts.append(example)
            labels.append(category)
    model = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), stop_words="english")),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]
    )
    model.fit(texts, labels)
    return model


def train_and_save_model(path: str | os.PathLike = MODEL_PATH):
    pipeline = build_model_pipeline()
    joblib.dump(pipeline, path)
    return pipeline


def load_model(path: str | os.PathLike = MODEL_PATH):
    if not os.path.exists(path):
        return train_and_save_model(path)
    return joblib.load(path)


def fallback_classification(logs: str):
    lowered = logs.lower()
    for keyword, config in FALLBACK_RULES.items():
        if keyword in lowered:
            return config
    if "database" in lowered or "postgres" in lowered or "sql" in lowered:
        return FALLBACK_RULES["database connection failure"]
    if "memory" in lowered or "oom" in lowered or "heap" in lowered:
        return FALLBACK_RULES["memory/resource problem"]
    if "timeout" in lowered or "network" in lowered or "socket" in lowered:
        return FALLBACK_RULES["network timeout"]
    if "exception" in lowered or "traceback" in lowered or "error" in lowered:
        return FALLBACK_RULES["application exception"]
    if "auth" in lowered or "jwt" in lowered or "token" in lowered or "401" in lowered or "403" in lowered:
        return FALLBACK_RULES["authentication failure"]
    if "dependency" in lowered or "build" in lowered or "module" in lowered or "install" in lowered:
        return FALLBACK_RULES["dependency/build failure"]
    return FALLBACK_RULES["application exception"]
''',
    'backend/app/services/log_classifier.py': r'''from app.config import settings
from app.ml.train_model import fallback_classification, load_model


def analyze_logs(logs: str) -> dict:
    cleaned = (logs or "").strip()
    if not cleaned:
        return {
            "category": "Unknown",
            "confidence": 0.0,
            "diagnosis": "No log content was provided for analysis.",
            "severity": "Medium",
        }

    model = load_model()
    prediction = model.predict([cleaned])[0]
    probability = float(model.predict_proba([cleaned])[0].max())

    if probability >= settings.ml_threshold:
        category = prediction
        severity = {
            "Database Connection Failure": "High",
            "Memory/Resource Problem": "High",
            "Network Timeout": "Medium",
            "Application Exception": "High",
            "Authentication Failure": "High",
            "Dependency/Build Failure": "Critical",
        }.get(category, "Medium")
        diagnosis = {
            "Database Connection Failure": "Database connection could not be established.",
            "Memory/Resource Problem": "Application resources or memory limits were exceeded.",
            "Network Timeout": "The service timed out while communicating with an upstream dependency.",
            "Application Exception": "An application exception caused the deployment to fail.",
            "Authentication Failure": "Authentication to a required service failed.",
            "Dependency/Build Failure": "Dependency resolution or a build step failed before application startup.",
        }.get(category, "The underlying issue requires a manual investigation.")
        return {
            "category": category,
            "confidence": round(probability, 3),
            "diagnosis": diagnosis,
            "severity": severity,
        }

    fallback = fallback_classification(cleaned)
    return {
        "category": fallback["category"],
        "confidence": round(probability, 3),
        "diagnosis": fallback["diagnosis"],
        "severity": fallback["severity"],
    }
''',
    'backend/app/routes/__init__.py': '',
    'backend/app/routes/applications.py': r'''from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationRead

router = APIRouter()


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    app_record = Application(
        name=payload.name,
        description=payload.description,
        repository_url=payload.repository_url,
        environment=payload.environment,
        created_at=datetime.utcnow(),
    )
    db.add(app_record)
    db.commit()
    db.refresh(app_record)
    return app_record


@router.get("", response_model=list[ApplicationRead])
def list_applications(db: Session = Depends(get_db)):
    return db.query(Application).order_by(Application.created_at.desc()).all()


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, db: Session = Depends(get_db)):
    record = db.query(Application).filter(Application.id == application_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")
    return record


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: Session = Depends(get_db)):
    record = db.query(Application).filter(Application.id == application_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(record)
    db.commit()
    return None
''',
    'backend/app/routes/deployments.py': r'''from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import Application
from app.models.deployment import Deployment
from app.schemas.deployment import DeploymentCreate, DeploymentRead
from app.services.deployment_engine import simulate_deployment
from app.services.incident_manager import create_incident_from_deployment

router = APIRouter()


@router.post("", response_model=DeploymentRead, status_code=status.HTTP_201_CREATED)
def create_deployment(payload: DeploymentCreate, db: Session = Depends(get_db)):
    app_record = db.query(Application).filter(Application.id == payload.application_id).first()
    if not app_record:
        raise HTTPException(status_code=404, detail="Application not found")

    supported = {
        "successful",
        "build_failure",
        "dependency_installation_failure",
        "application_startup_failure",
        "health_check_failure",
    }
    if payload.scenario.strip().lower().replace(" ", "_") not in supported:
        raise HTTPException(status_code=400, detail="Unsupported deployment scenario")

    simulation = simulate_deployment(payload.version, payload.scenario)
    record = Deployment(
        application_id=payload.application_id,
        version=simulation["version"],
        scenario=simulation["scenario"],
        status=simulation["status"],
        started_at=simulation["started_at"],
        completed_at=simulation["completed_at"],
        logs=simulation["logs"],
        failure_reason=simulation["failure_reason"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    if record.status.lower() == "failed":
        incident = create_incident_from_deployment(record, db)
        record.incident_id = incident.id
        db.commit()
        db.refresh(record)

    return record


@router.get("", response_model=list[DeploymentRead])
def list_deployments(db: Session = Depends(get_db)):
    return db.query(Deployment).order_by(Deployment.started_at.desc()).all()


@router.get("/{deployment_id}", response_model=DeploymentRead)
def get_deployment(deployment_id: int, db: Session = Depends(get_db)):
    record = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return record


@router.get("/application/{application_id}", response_model=list[DeploymentRead])
def get_app_deployments(application_id: int, db: Session = Depends(get_db)):
    return db.query(Deployment).filter(Deployment.application_id == application_id).order_by(Deployment.started_at.desc()).all()


@router.get("/application/{application_id}/deployments", response_model=list[DeploymentRead])
def get_app_deployments_alias(application_id: int, db: Session = Depends(get_db)):
    return get_app_deployments(application_id, db)
''',
    'backend/app/routes/incidents.py': r'''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.incident import Incident
from app.schemas.incident import IncidentPatch, IncidentRead
from app.services.log_classifier import analyze_logs

router = APIRouter()


@router.get("", response_model=list[IncidentRead])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.created_at.desc()).all()


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}", response_model=IncidentRead)
def patch_incident(incident_id: int, payload: IncidentPatch, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(incident, field, value)
    db.commit()
    db.refresh(incident)
    return incident


@router.post("/{incident_id}/analyze", response_model=IncidentRead)
def analyze_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    analysis = analyze_logs(incident.error_logs)
    incident.ml_category = analysis["category"]
    incident.ml_confidence = analysis["confidence"]
    incident.diagnosis = analysis["diagnosis"]
    incident.root_cause_category = analysis["category"]
    incident.severity = analysis["severity"]
    db.commit()
    db.refresh(incident)
    return incident
''',
    'backend/app/routes/analytics.py': r'''from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import Application
from app.models.deployment import Deployment
from app.models.incident import Incident

router = APIRouter()


@router.get("/overview")
def analytics_overview(db: Session = Depends(get_db)):
    total_applications = db.query(Application).count()
    total_deployments = db.query(Deployment).count()
    successful_deployments = db.query(Deployment).filter(Deployment.status == "Succeeded").count()
    failed_deployments = db.query(Deployment).filter(Deployment.status == "Failed").count()
    open_incidents = db.query(Incident).filter(Incident.status == "Open").count()
    resolved_incidents = db.query(Incident).filter(Incident.status == "Resolved").count()
    success_rate = 0.0
    if total_deployments:
        success_rate = round((successful_deployments / total_deployments) * 100, 2)
    return {
        "total_applications": total_applications,
        "total_deployments": total_deployments,
        "successful_deployments": successful_deployments,
        "failed_deployments": failed_deployments,
        "open_incidents": open_incidents,
        "resolved_incidents": resolved_incidents,
        "deployment_success_rate": success_rate,
    }
''',
    'backend/app/routes/monitoring.py': r'''from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import Application
from app.models.deployment import Deployment
from app.models.incident import Incident

router = APIRouter()


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    total_applications = db.query(Application).count()
    total_deployments = db.query(Deployment).count()
    total_incidents = db.query(Incident).count()
    return {
        "applications": total_applications,
        "deployments": total_deployments,
        "incidents": total_incidents,
        "healthy": total_applications > 0,
    }
''',
    'backend/tests/test_api.py': r'''from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_application_registration_and_retrieval():
    response = client.post("/applications", json={
        "name": "frontend-api",
        "description": "Payments service",
        "repository_url": "https://github.com/example/payments",
        "environment": "prod",
    })
    assert response.status_code == 201
    payload = response.json()
    app_id = payload["id"]
    assert payload["name"] == "frontend-api"

    retrieval = client.get(f"/applications/{app_id}")
    assert retrieval.status_code == 200
    assert retrieval.json()["id"] == app_id


def test_invalid_application_input():
    response = client.post("/applications", json={
        "name": "a",
        "environment": "prod",
    })
    assert response.status_code == 422


def test_successful_deployment_creates_no_incident():
    app_response = client.post("/applications", json={
        "name": "worker-app",
        "description": "Background worker",
        "environment": "staging",
    })
    app_id = app_response.json()["id"]
    response = client.post("/deployments", json={
        "application_id": app_id,
        "version": "v1.2.0",
        "scenario": "successful",
    })
    assert response.status_code == 201
    assert response.json()["status"] == "Succeeded"


def test_failed_deployment_creates_incident():
    app_response = client.post("/applications", json={
        "name": "api-failure",
        "description": "Failing API app",
        "environment": "dev",
    })
    app_id = app_response.json()["id"]
    response = client.post("/deployments", json={
        "application_id": app_id,
        "version": "v2.0.0",
        "scenario": "build_failure",
    })
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "Failed"
    assert payload["incident_id"] is not None

    incident = client.get(f"/incidents/{payload['incident_id']}")
    assert incident.status_code == 200
    assert incident.json()["status"] == "Open"


def test_incident_status_update():
    app_response = client.post("/applications", json={
        "name": "incident-update",
        "description": "Example incident into investigation",
        "environment": "dev",
    })
    dep = client.post("/deployments", json={
        "application_id": app_response.json()["id"],
        "version": "v3.1.0",
        "scenario": "health_check_failure",
    })
    incident_id = dep.json()["incident_id"]
    patch = client.patch(f"/incidents/{incident_id}", json={"status": "Investigating"})
    assert patch.status_code == 200
    assert patch.json()["status"] == "Investigating"


def test_analytics_overview():
    response = client.get("/analytics/overview")
    assert response.status_code == 200
    payload = response.json()
    assert "total_applications" in payload
    assert "deployment_success_rate" in payload


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.json()["applications"] >= 0


def test_application_deployments_endpoint():
    app_response = client.post("/applications", json={
        "name": "deployments-list",
        "description": "Multiple deployments",
        "environment": "prod",
    })
    app_id = app_response.json()["id"]
    client.post("/deployments", json={"application_id": app_id, "version": "v1", "scenario": "successful"})
    client.post("/deployments", json={"application_id": app_id, "version": "v2", "scenario": "build_failure"})
    response = client.get(f"/applications/{app_id}/deployments")
    assert response.status_code == 200
    assert len(response.json()) >= 2
''',
    '.gitignore': r'''__pycache__/
*.pyc
.venv/
.env
backend/.pytest_cache/
frontend/node_modules/
frontend/dist/
backend/nexusops.db
.DS_Store
''',
    '.env.example': r'''BACKEND_PORT=8000
FRONTEND_PORT=5173
VITE_API_URL=http://localhost:8000
DATABASE_URL=sqlite:///./nexusops.db
ML_THRESHOLD=0.55
''',
    'docker-compose.yml': r'''version: "3.9"

services:
  backend:
    build:
      context: ./backend
    container_name: nexusops-backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: sqlite:///./nexusops.db
      CORS_ORIGINS: "[\"http://localhost:5173\",\"http://127.0.0.1:5173\"]"
    volumes:
      - ./backend:/app
      - sqlite_data:/app
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"]
      interval: 10s
      timeout: 5s
      retries: 5

  frontend:
    build:
      context: ./frontend
    container_name: nexusops-frontend
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app

volumes:
  sqlite_data:
''',
    'README.md': r'''# NexusOps Lite

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
''',
    '.github/workflows/ci.yml': r'''name: NexusOps Lite CI

on:
  push:
  pull_request:

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
      - name: Install backend dependencies
        run: pip install -r backend/requirements.txt
      - name: Run backend tests
        run: cd backend && pytest -q

  frontend:
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v4
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - name: Install frontend dependencies
        working-directory: frontend
        run: npm install
      - name: Run frontend build
        working-directory: frontend
        run: npm run build
''',
    'infrastructure/terraform/main.tf': r'''terraform {
  required_version = ">= 1.5.0"
}

variable "project_name" {
  description = "Name of the deployment project"
  type        = string
  default     = "nexusops-lite"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

locals {
  deployment_label = "${var.project_name}-${var.environment}"
}

output "deployment_label" {
  description = "The deployment label that would be used for local platform configuration"
  value       = local.deployment_label
}

output "summary" {
  description = "Terraform summary for this demonstration infrastructure"
  value       = "This configuration demonstrates the local infrastructure footprint required for ${local.deployment_label}."
}
''',
    'infrastructure/terraform/variables.tf': r'''variable "project_name" {
  description = "Project identifier"
  type        = string
  default     = "nexusops-lite"
}

variable "environment" {
  description = "Target environment"
  type        = string
  default     = "dev"
}
''',
    'infrastructure/terraform/outputs.tf': r'''output "project_name" {
  description = "Terraform project name"
  value       = var.project_name
}

output "environment" {
  description = "Terraform environment name"
  value       = var.environment
}
''',
    'infrastructure/terraform/README.md': r'''# Terraform configuration

This folder contains a safe, locally validatable Terraform example for the NexusOps Lite platform. It is intentionally lightweight and does not require AWS credentials or paid infrastructure.

The configuration documents the project name and environment, which represent the local deployment metadata that a real infrastructure definition would use.

## Validate locally

```powershell
cd C:\Users\baijunath karvir\Desktop\Nexus_Ops\NexusOps-Lite\ninfrastructure\terraform
terraform fmt
terraform validate
```

This configuration is intentionally non-destructive and does not call `terraform apply`.
''',
    'frontend/package.json': r'''{
  "name": "nexusops-lite-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview --host 0.0.0.0",
    "lint": "eslint . --ext ts,tsx --max-warnings 0"
  },
  "dependencies": {
    "axios": "^1.8.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0"
  },
  "devDependencies": {
    "@eslint/js": "^9.17.0",
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.4",
    "autoprefixer": "^10.4.20",
    "eslint": "^9.17.0",
    "eslint-plugin-react": "^7.0.0",
    "eslint-plugin-react-hooks": "^5.0.0",
    "eslint-plugin-react-refresh": "^0.4.0",
    "postcss": "^8.4.49",
    "tailwindcss": "^3.4.16",
    "typescript": "^5.6.3",
    "vite": "^5.4.10"
  }
}
''',
    'frontend/tsconfig.json': r'''{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}
''',
    'frontend/tsconfig.app.json': r'''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "allowJs": false,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"],
  "exclude": ["src/**/*.test.*"]
}
''',
    'frontend/tsconfig.node.json': r'''{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "Node",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
''',
    'frontend/vite.config.ts': r'''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
  },
  preview: {
    host: '0.0.0.0',
    port: 4173,
  },
  define: {
    'process.env': {},
  },
});
''',
    'frontend/index.html': r'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>NexusOps Lite</title>
  </head>
  <body class="bg-slate-950">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
''',
    'frontend/postcss.config.js': r'''export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
''',
    'frontend/tailwind.config.js': r'''/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
};
''',
    'frontend/src/main.tsx': r'''import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
);
''',
    'frontend/src/index.css': r'''@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  font-family: Inter, system-ui, sans-serif;
  color: #e2e8f0;
  background: #020817;
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
  background: linear-gradient(135deg, #020817 0%, #111827 100%);
}

* {
  box-sizing: border-box;
}

button, input, select, textarea {
  font: inherit;
}
''',
    'frontend/src/types/index.ts': r'''export type Application = {
  id: number;
  name: string;
  description: string;
  repository_url?: string | null;
  environment: string;
  created_at: string;
};

export type Deployment = {
  id: number;
  application_id: number;
  version: string;
  scenario: string;
  status: string;
  started_at: string;
  completed_at?: string | null;
  logs: string;
  failure_reason?: string | null;
  incident_id?: number | null;
};

export type Incident = {
  id: number;
  deployment_id: number;
  severity: string;
  error_logs: string;
  root_cause_category: string;
  diagnosis: string;
  recommended_resolution: string;
  status: string;
  created_at: string;
  ml_category?: string | null;
  ml_confidence?: number | null;
};

export type Overview = {
  total_applications: number;
  total_deployments: number;
  successful_deployments: number;
  failed_deployments: number;
  open_incidents: number;
  resolved_incidents: number;
  deployment_success_rate: number;
};
''',
    'frontend/src/services/api.ts': r'''import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
});

export async function getOverview() {
  const { data } = await api.get('/analytics/overview');
  return data;
}

export async function getHealth() {
  const { data } = await api.get('/health');
  return data;
}

export async function getMetrics() {
  const { data } = await api.get('/metrics');
  return data;
}

export async function listApplications() {
  const { data } = await api.get('/applications');
  return data;
}

export async function createApplication(payload: Record<string, string>) {
  const { data } = await api.post('/applications', payload);
  return data;
}

export async function listDeployments() {
  const { data } = await api.get('/deployments');
  return data;
}

export async function createDeployment(payload: Record<string, string | number>) {
  const { data } = await api.post('/deployments', payload);
  return data;
}

export async function listIncidents() {
  const { data } = await api.get('/incidents');
  return data;
}

export async function updateIncident(id: number, payload: Record<string, string>) {
  const { data } = await api.patch(`/incidents/${id}`, payload);
  return data;
}

export async function analyzeIncident(id: number) {
  const { data } = await api.post(`/incidents/${id}/analyze`);
  return data;
}
''',
    'frontend/src/components/StatCard.tsx': r'''type Props = { title: string; value: string; accent?: string };

export default function StatCard({ title, value, accent = 'bg-slate-800' }: Props) {
  return (
    <div className={`${accent} rounded-xl border border-slate-700 p-4 shadow-lg`}>
      <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{title}</p>
      <h3 className="mt-3 text-2xl font-semibold text-white">{value}</h3>
    </div>
  );
}
''',
    'frontend/src/components/Layout.tsx': r'''import { NavLink, Outlet } from 'react-router-dom';

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/applications', label: 'Applications' },
  { to: '/deployments', label: 'Deployments' },
  { to: '/incidents', label: 'Incidents' },
  { to: '/monitoring', label: 'Monitoring' },
  { to: '/about', label: 'About' },
];

export default function Layout() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <aside className="fixed inset-y-0 left-0 w-64 border-r border-slate-800 bg-slate-900/80 p-5 backdrop-blur">
        <div className="mb-8">
          <p className="text-sm uppercase tracking-[0.3em] text-cyan-400">NexusOps</p>
          <h1 className="mt-2 text-2xl font-bold text-white">Lite</h1>
        </div>
        <nav className="space-y-2">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-300 hover:bg-slate-800'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="ml-64 p-8">
        <Outlet />
      </main>
    </div>
  );
}
''',
    'frontend/src/App.tsx': r'''import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import ApplicationsPage from './pages/ApplicationsPage';
import DeploymentsPage from './pages/DeploymentsPage';
import IncidentsPage from './pages/IncidentsPage';
import MonitoringPage from './pages/MonitoringPage';
import AboutPage from './pages/AboutPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/applications" element={<ApplicationsPage />} />
        <Route path="/deployments" element={<DeploymentsPage />} />
        <Route path="/incidents" element={<IncidentsPage />} />
        <Route path="/monitoring" element={<MonitoringPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
''',
    'frontend/src/pages/DashboardPage.tsx': r'''import { useEffect, useState } from 'react';
import StatCard from '../components/StatCard';
import { getHealth, getOverview } from '../services/api';
import type { Overview } from '../types';

export default function DashboardPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [health, setHealth] = useState<{ status?: string } | null>(null);

  useEffect(() => {
    Promise.all([getOverview(), getHealth()]).then(([data, healthData]) => {
      setOverview(data);
      setHealth(healthData);
    });
  }, []);

  if (!overview) {
    return <div className="text-slate-300">Loading dashboard…</div>;
  }

  return (
    <div className="space-y-8">
      <header className="flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-cyan-400">Operations</p>
          <h2 className="mt-2 text-3xl font-bold text-white">Dashboard</h2>
        </div>
        <div className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-sm text-emerald-300">
          {health?.status === 'ok' ? 'Service healthy' : 'Checking health'}
        </div>
      </header>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        <StatCard title="Applications" value={String(overview.total_applications)} accent="bg-slate-800" />
        <StatCard title="Deployments" value={String(overview.total_deployments)} accent="bg-slate-800" />
        <StatCard title="Success %" value={`${overview.deployment_success_rate}%`} accent="bg-emerald-900/50" />
        <StatCard title="Open incidents" value={String(overview.open_incidents)} accent="bg-amber-900/40" />
        <StatCard title="Resolved" value={String(overview.resolved_incidents)} accent="bg-cyan-900/40" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
          <h3 className="mb-4 text-lg font-semibold text-white">Deployment summary</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm text-slate-300"><span>Succeeded</span><span>{overview.successful_deployments}</span></div>
            <div className="flex items-center justify-between text-sm text-slate-300"><span>Failed</span><span>{overview.failed_deployments}</span></div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-800">
              <div className="h-full rounded-full bg-emerald-500" style={{ width: `${overview.deployment_success_rate}%` }} />
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
          <h3 className="mb-4 text-lg font-semibold text-white">Incident severity</h3>
          <ul className="space-y-2 text-sm text-slate-300">
            <li>Open incidents: {overview.open_incidents}</li>
            <li>Resolved incidents: {overview.resolved_incidents}</li>
            <li>Failed deployments: {overview.failed_deployments}</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
''',
    'frontend/src/pages/ApplicationsPage.tsx': r'''import { useEffect, useState } from 'react';
import { createApplication, listApplications } from '../services/api';
import type { Application } from '../types';

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [form, setForm] = useState({ name: '', description: '', repository_url: '', environment: 'dev' });

  const load = async () => {
    const data = await listApplications();
    setApplications(data);
  };

  useEffect(() => {
    load();
  }, []);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await createApplication(form);
    setForm({ name: '', description: '', repository_url: '', environment: 'dev' });
    await load();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Applications</h2>

      <form onSubmit={onSubmit} className="rounded-xl border border-slate-700 bg-slate-900 p-5 space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <input className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="App name" required />
          <select className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.environment} onChange={(e) => setForm({ ...form, environment: e.target.value })}>
            <option value="dev">Development</option>
            <option value="staging">Staging</option>
            <option value="prod">Production</option>
          </select>
        </div>
        <input className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.repository_url} onChange={(e) => setForm({ ...form, repository_url: e.target.value })} placeholder="Repository URL" />
        <textarea className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Description" rows={3} />
        <button type="submit" className="rounded-lg bg-cyan-500 px-4 py-2 font-semibold text-slate-950">Register application</button>
      </form>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {applications.map((app) => (
          <div key={app.id} className="rounded-xl border border-slate-700 bg-slate-900 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">{app.environment}</p>
            <h3 className="mt-2 text-xl font-semibold text-white">{app.name}</h3>
            <p className="mt-2 text-sm text-slate-300">{app.description || 'No description provided.'}</p>
            <p className="mt-4 text-xs text-slate-400">{app.repository_url || 'No repository URL'}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
''',
    'frontend/src/pages/DeploymentsPage.tsx': r'''import { useEffect, useState } from 'react';
import { createDeployment, listApplications, listDeployments } from '../services/api';
import type { Application, Deployment } from '../types';

const scenarios = ['successful', 'build_failure', 'dependency_installation_failure', 'application_startup_failure', 'health_check_failure'];

export default function DeploymentsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [form, setForm] = useState({ application_id: '', version: 'v1.0.0', scenario: 'successful' });

  const load = async () => {
    const [apps, depData] = await Promise.all([listApplications(), listDeployments()]);
    setApplications(apps);
    setDeployments(depData);
  };

  useEffect(() => {
    load();
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.application_id) return;
    await createDeployment({ application_id: Number(form.application_id), version: form.version, scenario: form.scenario });
    setForm({ application_id: form.application_id, version: form.version, scenario: form.scenario });
    await load();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Deployments</h2>

      <form onSubmit={handleSubmit} className="rounded-xl border border-slate-700 bg-slate-900 p-5 space-y-4">
        <div className="grid gap-4 md:grid-cols-3">
          <select className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.application_id} onChange={(e) => setForm({ ...form, application_id: e.target.value })}>
            <option value="">Select application</option>
            {applications.map((app) => (
              <option key={app.id} value={app.id}>{app.name}</option>
            ))}
          </select>
          <input className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.version} onChange={(e) => setForm({ ...form, version: e.target.value })} placeholder="Version" />
          <select className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" value={form.scenario} onChange={(e) => setForm({ ...form, scenario: e.target.value })}>
            {scenarios.map((scenario) => (
              <option key={scenario} value={scenario}>{scenario}</option>
            ))}
          </select>
        </div>
        <button type="submit" className="rounded-lg bg-emerald-500 px-4 py-2 font-semibold text-slate-950">Trigger deployment</button>
      </form>

      <div className="space-y-4">
        {deployments.map((deployment) => (
          <div key={deployment.id} className="rounded-xl border border-slate-700 bg-slate-900 p-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-cyan-400">{deployment.scenario}</p>
                <h3 className="text-xl font-semibold text-white">Version {deployment.version}</h3>
              </div>
              <span className={`rounded-full px-2 py-1 text-xs ${deployment.status === 'Succeeded' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}`}>
                {deployment.status}
              </span>
            </div>
            <pre className="mt-4 overflow-auto rounded-lg bg-slate-950 p-3 text-xs text-slate-300">{deployment.logs}</pre>
          </div>
        ))}
      </div>
    </div>
  );
}
''',
    'frontend/src/pages/IncidentsPage.tsx': r'''import { useEffect, useState } from 'react';
import { analyzeIncident, listIncidents, updateIncident } from '../services/api';
import type { Incident } from '../types';

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);

  const load = async () => {
    const data = await listIncidents();
    setIncidents(data);
  };

  useEffect(() => {
    load();
  }, []);

  const onStatusUpdate = async (incidentId: number, status: string) => {
    await updateIncident(incidentId, { status });
    await load();
  };

  const onAnalyze = async (incidentId: number) => {
    await analyzeIncident(incidentId);
    await load();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Incidents</h2>
      <div className="space-y-4">
        {incidents.map((incident) => (
          <div key={incident.id} className="rounded-xl border border-slate-700 bg-slate-900 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-amber-400">{incident.severity}</p>
                <h3 className="mt-2 text-xl font-semibold text-white">Incident #{incident.id}</h3>
              </div>
              <div className="space-x-2 text-sm">
                <button className="rounded-lg bg-cyan-500 px-3 py-1 font-semibold text-slate-900" onClick={() => onAnalyze(incident.id)}>Analyze</button>
                <button className="rounded-lg border border-slate-600 bg-slate-800 px-3 py-1" onClick={() => onStatusUpdate(incident.id, incident.status === 'Open' ? 'Investigating' : 'Resolved')}>Toggle status</button>
              </div>
            </div>
            <p className="mt-4 text-slate-300">{incident.diagnosis || 'No diagnosis yet.'}</p>
            <p className="mt-2 text-sm text-cyan-300">Recommendation: {incident.recommended_resolution || 'Not available.'}</p>
            <pre className="mt-4 overflow-auto rounded-lg bg-slate-950 p-3 text-xs text-slate-300">{incident.error_logs}</pre>
          </div>
        ))}
      </div>
    </div>
  );
}
''',
    'frontend/src/pages/MonitoringPage.tsx': r'''import { useEffect, useState } from 'react';
import { getHealth, getMetrics, getOverview } from '../services/api';

export default function MonitoringPage() {
  const [overview, setOverview] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    Promise.all([getOverview(), getMetrics(), getHealth()]).then(([overviewData, metricsData, healthData]) => {
      setOverview(overviewData);
      setMetrics(metricsData);
      setHealth(healthData);
    });
  }, []);

  if (!overview || !metrics) return <div className="text-slate-300">Loading monitoring data…</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">Monitoring</h2>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-5"><p className="text-xs uppercase text-cyan-400">Health</p><h3 className="mt-3 text-2xl">{health?.status}</h3></div>
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-5"><p className="text-xs uppercase text-cyan-400">Applications</p><h3 className="mt-3 text-2xl">{metrics.applications}</h3></div>
        <div className="rounded-xl border border-slate-700 bg-slate-900 p-5"><p className="text-xs uppercase text-cyan-400">Deployments</p><h3 className="mt-3 text-2xl">{metrics.deployments}</h3></div>
      </div>
      <div className="rounded-xl border border-slate-700 bg-slate-900 p-5">
        <h3 className="mb-4 text-lg font-semibold text-white">Overview</h3>
        <ul className="space-y-2 text-slate-300">
          <li>Successful deployments: {overview.successful_deployments}</li>
          <li>Failed deployments: {overview.failed_deployments}</li>
          <li>Open incidents: {overview.open_incidents}</li>
          <li>Success rate: {overview.deployment_success_rate}%</li>
        </ul>
      </div>
    </div>
  );
}
''',
    'frontend/src/pages/AboutPage.tsx': r'''export default function AboutPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-white">About NexusOps Lite</h2>
      <div className="rounded-xl border border-slate-700 bg-slate-900 p-5 text-slate-300">
        <p className="mb-4">NexusOps Lite is a local-first DevOps dashboard that simulates deployments, records incidents, and provides lightweight ML-driven diagnostics for logs.</p>
        <ul className="list-disc space-y-2 pl-5">
          <li>Version: 0.1.0</li>
          <li>Deployment simulation: deterministic and reproducible</li>
          <li>Stack: FastAPI, SQLAlchemy, React, TypeScript, Vite, Tailwind CSS, scikit-learn</li>
          <li>Purpose: interview-friendly demonstration of backend engineering and DevOps workflows</li>
        </ul>
      </div>
    </div>
  );
}
''',
    'frontend/Dockerfile': r'''FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
''',
}

for relative_path, content in files.items():
    target = base / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8')

print('Created project layout with', len(files), 'files')
