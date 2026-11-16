LOG_TRAINING_DATA = {
    "Database Connection Failure": [
        "ERROR: Unable to connect to PostgreSQL database. Connection timed out.",
        "FATAL: Database connection refused while connecting to the primary instance.",
        "SQLAlchemy OperationalError: could not connect to server: Connection refused.",
        "ERROR: database host unreachable after migration rollout.",
        "Database connection error: password authentication failed for app_user.",
    ],
    "Memory/Resource Problem": [
        "OutOfMemoryError: Java heap space exhausted during deployment.",
        "ERROR: container memory limit reached while starting background workers.",
        "Killed process due to high memory pressure from the application container.",
        "Resource temporarily unavailable while allocating memory for cache.",
        "The service ran out of memory and restarted unexpectedly.",
    ],
    "Network Timeout": [
        "Timeout connecting to upstream API service after 30 seconds.",
        "ERROR: network timeout while fetching metadata from edge gateway.",
        "Socket timeout reading response from third-party service.",
        "HTTP request failed due to connectivity issue and timeout.",
        "Gateway response timed out while waiting for backend service.",
    ],
    "Application Exception": [
        "Traceback: ValueError: invalid response payload from parser.",
        "Unhandled exception in worker thread: KeyError on session state.",
        "ERROR: application crash caused by unexpected None value.",
        "Exception in api route: TypeError: unsupported operand for object.",
        "Runtime exception thrown while processing upload request.",
    ],
    "Authentication Failure": [
        "401 Unauthorized token expired while authenticating service account.",
        "Authentication failed for user session after JWT refresh.",
        "Permission denied: access token invalid for the requested service.",
        "ERROR: SSO callback rejected due to invalid credentials.",
        "Authentication server returned 403 forbidden for the service principal.",
    ],
    "Dependency/Build Failure": [
        "ERROR: Build failed because the package manager could not install dependency.",
        "ModuleNotFoundError: missing package while compiling the release artifact.",
        "Dependency resolution failed during build step before startup.",
        "Failed to install project dependencies and aborted release pipeline.",
        "Compilation error: dependency version mismatch in requirements file.",
    ],
}

FALLBACK_RULES = {
    "database connection failure": {
        "category": "Database Connection Failure",
        "severity": "High",
        "diagnosis": "Database connection could not be established.",
        "recommendation": "Verify database host, port, credentials, and service availability.",
    },
    "memory/resource problem": {
        "category": "Memory/Resource Problem",
        "severity": "High",
        "diagnosis": "Application memory or resource limits were exceeded.",
        "recommendation": "Increase memory limits, inspect memory usage, and trim unnecessary cache allocations.",
    },
    "network timeout": {
        "category": "Network Timeout",
        "severity": "Medium",
        "diagnosis": "The application timed out while contacting an upstream dependency.",
        "recommendation": "Review networking policy, DNS resolution, and timeout settings for upstream services.",
    },
    "application exception": {
        "category": "Application Exception",
        "severity": "High",
        "diagnosis": "An application-level exception caused the release to fail.",
        "recommendation": "Inspect the traceback, validate runtime inputs, and confirm the application is resilient to bad payloads.",
    },
    "authentication failure": {
        "category": "Authentication Failure",
        "severity": "High",
        "diagnosis": "The application could not authenticate to a required service.",
        "recommendation": "Validate tokens, credentials, and identity configuration before retrying the deployment.",
    },
    "dependency/build failure": {
        "category": "Dependency/Build Failure",
        "severity": "Critical",
        "diagnosis": "Dependency resolution or build tooling failed before the application could start.",
        "recommendation": "Check dependency versions, lock files, and build environment settings before rerunning the pipeline.",
    },
}
