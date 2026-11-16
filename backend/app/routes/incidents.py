from fastapi import APIRouter, Depends, HTTPException
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
