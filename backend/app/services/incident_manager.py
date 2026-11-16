from app.models.incident import Incident
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
