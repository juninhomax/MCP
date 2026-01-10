from fastapi import FastAPI, HTTPException
from slaves.windows.config import settings
from slaves.windows.executor import WindowsExecutor
from slaves.windows.tools.registry import registry, register_windows_tools
from shared.protocol.jsonrpc import JSONRPCRequest, JSONRPCResponse, JSONRPCError, JSONRPCErrorCode
from shared.schemas.tool_schema import ToolExecutionRequest
import structlog
import httpx

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
    description="MCP Slave Windows - Execution Agent",
    version="0.1.0"
)

executor = WindowsExecutor()


@app.on_event("startup")
async def startup_event():
    register_windows_tools()
    logger.info(
        "slave_starting",
        slave_id=settings.slave_id,
        slave_type=settings.slave_type,
        port=settings.port
    )
    
    if settings.auth_token and settings.brain_endpoint:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.brain_endpoint}/api/v1/slaves/register",
                    json={
                        "slave_id": settings.slave_id,
                        "slave_type": settings.slave_type,
                        "endpoint": f"http://{settings.host}:{settings.port}",
                        "capabilities": [tool.name for tool in registry.list_tools()]
                    },
                    headers={"Authorization": f"Bearer {settings.auth_token}"}
                )
                if response.status_code == 200:
                    logger.info("registered_with_brain", brain=settings.brain_endpoint)
        except Exception as e:
            logger.warning("brain_registration_failed", error=str(e))


@app.post("/jsonrpc")
async def jsonrpc_handler(request: JSONRPCRequest):
    logger.info("jsonrpc_request", method=request.method, id=request.id)
    
    if request.method == "execute_tool":
        try:
            params = request.params or {}
            tool_name = params.get("tool_name")
            parameters = params.get("parameters", {})
            dry_run = params.get("dry_run", False)
            
            if not tool_name:
                return JSONRPCResponse(
                    error=JSONRPCError(
                        code=JSONRPCErrorCode.INVALID_PARAMS,
                        message="Missing tool_name parameter"
                    ),
                    id=request.id
                )
            
            result = await executor.execute_tool(tool_name, parameters, dry_run)
            
            return JSONRPCResponse(
                result=result.model_dump(),
                id=request.id
            )
            
        except Exception as e:
            logger.error("execution_error", error=str(e))
            return JSONRPCResponse(
                error=JSONRPCError(
                    code=JSONRPCErrorCode.EXECUTION_FAILED,
                    message=str(e)
                ),
                id=request.id
            )
    
    elif request.method == "list_tools":
        tools = [tool.model_dump() for tool in registry.list_tools()]
        return JSONRPCResponse(result={"tools": tools}, id=request.id)
    
    else:
        return JSONRPCResponse(
            error=JSONRPCError(
                code=JSONRPCErrorCode.METHOD_NOT_FOUND,
                message=f"Method not found: {request.method}"
            ),
            id=request.id
        )


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "slave_id": settings.slave_id,
        "slave_type": settings.slave_type
    }


@app.get("/tools")
async def list_tools():
    return {"tools": [tool.model_dump() for tool in registry.list_tools()]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=False
    )
