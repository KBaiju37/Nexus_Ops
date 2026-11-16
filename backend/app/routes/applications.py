from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.application import Application
from app.models.deployment import Deployment
from app.schemas.application import ApplicationCreate, ApplicationRead
from app.schemas.deployment import DeploymentRead

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


@router.get("/{application_id}/deployments", response_model=list[DeploymentRead])
def list_application_deployments(application_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return (
        db.query(Deployment)
        .filter(Deployment.application_id == application_id)
        .order_by(Deployment.started_at.desc())
        .all()
    )


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: Session = Depends(get_db)):
    record = db.query(Application).filter(Application.id == application_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(record)
    db.commit()
    return None
