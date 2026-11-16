from app.ml.train_model import FALLBACK_RULES


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
