from fastapi import APIRouter, Depends
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
