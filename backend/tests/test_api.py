from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_application_registration_and_retrieval():
    with TestClient(app) as client:
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
    with TestClient(app) as client:
        response = client.post("/applications", json={
            "name": "a",
            "environment": "prod",
        })
        assert response.status_code == 422


def test_successful_deployment_creates_no_incident():
    with TestClient(app) as client:
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
    with TestClient(app) as client:
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
    with TestClient(app) as client:
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
    with TestClient(app) as client:
        response = client.get("/analytics/overview")
        assert response.status_code == 200
        payload = response.json()
        assert "total_applications" in payload
        assert "deployment_success_rate" in payload


def test_metrics_endpoint():
    with TestClient(app) as client:
        response = client.get("/metrics")
        assert response.status_code == 200
        assert response.json()["applications"] >= 0


def test_application_deployments_endpoint():
    with TestClient(app) as client:
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
