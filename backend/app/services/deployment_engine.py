from datetime import datetime, timedelta

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
