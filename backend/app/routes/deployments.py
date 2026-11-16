from fastapi import APIRouter, Depends, HTTPException, status
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
