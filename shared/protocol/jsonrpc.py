from typing import Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class JSONRPCVersion(str, Enum):
    V2 = "2.0"


class JSONRPCRequest(BaseModel):
    jsonrpc: JSONRPCVersion = Field(default=JSONRPCVersion.V2)
    method: str
    params: Optional[dict[str, Any]] = None
    id: Union[str, int]


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class JSONRPCResponse(BaseModel):
    jsonrpc: JSONRPCVersion = Field(default=JSONRPCVersion.V2)
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None
    id: Union[str, int, None]


class JSONRPCErrorCode(int, Enum):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR = -32000
    UNAUTHORIZED = -32001
    FORBIDDEN = -32002
    EXECUTION_FAILED = -32003
