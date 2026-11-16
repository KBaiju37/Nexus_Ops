from app.config import settings
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
