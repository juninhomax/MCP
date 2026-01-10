from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from brain.api.routes import router
from brain.config import settings
import structlog
import sys

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title=settings.app_name,
    description="MCP Brain - Distributed AI Infrastructure Orchestrator",
    version="0.1.0",
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    logger.info(
        "brain_starting",
        host=settings.brain_host,
        port=settings.brain_port,
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model
    )


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("brain_shutting_down")


@app.get("/")
async def root():
    return {
        "service": "MCP Brain",
        "version": "0.1.0",
        "status": "operational",
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.brain_host,
        port=settings.brain_port,
        reload=settings.debug
    )
