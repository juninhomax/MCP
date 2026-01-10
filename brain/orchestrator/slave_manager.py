from typing import Optional, Any
import httpx
from brain.models.task import SlaveInfo
from shared.protocol.jsonrpc import JSONRPCRequest, JSONRPCResponse
from shared.schemas.tool_schema import ToolExecutionRequest
import structlog

logger = structlog.get_logger()


class SlaveManager:
    def __init__(self):
        self.slaves: dict[str, SlaveInfo] = {}
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client
    
    def register_slave(self, slave_info: SlaveInfo):
        self.slaves[slave_info.slave_id] = slave_info
        logger.info(
            "slave_registered",
            slave_id=slave_info.slave_id,
            slave_type=slave_info.slave_type,
            endpoint=slave_info.endpoint
        )
    
    def get_slave_by_type(self, slave_type: str) -> Optional[SlaveInfo]:
        for slave in self.slaves.values():
            if slave.slave_type == slave_type and slave.status == "online":
                return slave
        return None
    
    async def execute_tool(
        self,
        slave_type: str,
        tool_name: str,
        parameters: dict[str, Any],
        dry_run: bool = False,
        timeout: int = 30
    ) -> dict[str, Any]:
        slave = self.get_slave_by_type(slave_type)
        if not slave:
            logger.error("no_slave_available", slave_type=slave_type)
            return {
                "success": False,
                "error": f"No {slave_type} slave available"
            }
        
        request = JSONRPCRequest(
            method="execute_tool",
            params={
                "tool_name": tool_name,
                "parameters": parameters,
                "dry_run": dry_run,
                "timeout": timeout
            },
            id=f"brain_{slave_type}_{tool_name}"
        )
        
        try:
            client = await self._get_client()
            response = await client.post(
                f"{slave.endpoint}/jsonrpc",
                json=request.model_dump(),
                timeout=timeout + 5
            )
            response.raise_for_status()
            
            rpc_response = JSONRPCResponse(**response.json())
            
            if rpc_response.error:
                logger.error(
                    "slave_execution_error",
                    slave_id=slave.slave_id,
                    tool=tool_name,
                    error=rpc_response.error.message
                )
                return {
                    "success": False,
                    "error": rpc_response.error.message
                }
            
            return rpc_response.result
            
        except httpx.HTTPError as e:
            logger.error(
                "slave_communication_error",
                slave_id=slave.slave_id,
                error=str(e)
            )
            return {
                "success": False,
                "error": f"Communication error: {str(e)}"
            }
    
    async def health_check(self, slave_id: str) -> bool:
        slave = self.slaves.get(slave_id)
        if not slave:
            return False
        
        try:
            client = await self._get_client()
            response = await client.get(f"{slave.endpoint}/health", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False
    
    async def close(self):
        if self._http_client:
            await self._http_client.aclose()
