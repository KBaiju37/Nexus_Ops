from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routes.analytics import router as analytics_router
from app.routes.applications import router as applications_router
from app.routes.deployments import router as deployments_router
from app.routes.incidents import router as incidents_router
from app.routes.monitoring import router as monitoring_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Local-first deployment monitoring and incident diagnosis platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications_router, prefix="/applications", tags=["applications"])
app.include_router(deployments_router, prefix="/deployments", tags=["deployments"])
app.include_router(incidents_router, prefix="/incidents", tags=["incidents"])
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(monitoring_router, tags=["monitoring"])


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}


@app.get("/")
def root():
    return {"name": settings.app_name, "status": "running"}
