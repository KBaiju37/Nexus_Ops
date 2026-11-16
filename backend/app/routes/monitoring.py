from fastapi import APIRouter, Depends
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
