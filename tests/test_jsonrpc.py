import pytest
from shared.protocol.jsonrpc import (
    JSONRPCRequest, 
    JSONRPCResponse, 
    JSONRPCError, 
    JSONRPCErrorCode,
    JSONRPCVersion
)


class TestJSONRPC:
    def test_create_request(self):
        request = JSONRPCRequest(
            method="execute_tool",
            params={"tool_name": "test"},
            id="123"
        )
        
        assert request.jsonrpc == JSONRPCVersion.V2
        assert request.method == "execute_tool"
        assert request.params["tool_name"] == "test"
        assert request.id == "123"
    
    def test_create_response_success(self):
        response = JSONRPCResponse(
            result={"status": "ok"},
            id="123"
        )
        
        assert response.jsonrpc == JSONRPCVersion.V2
        assert response.result["status"] == "ok"
        assert response.error is None
        assert response.id == "123"
    
    def test_create_response_error(self):
        error = JSONRPCError(
            code=JSONRPCErrorCode.METHOD_NOT_FOUND,
            message="Method not found"
        )
        
        response = JSONRPCResponse(
            error=error,
            id="123"
        )
        
        assert response.error is not None
        assert response.error.code == JSONRPCErrorCode.METHOD_NOT_FOUND
        assert response.error.message == "Method not found"
        assert response.result is None
    
    def test_error_codes(self):
        assert JSONRPCErrorCode.PARSE_ERROR == -32700
        assert JSONRPCErrorCode.INVALID_REQUEST == -32600
        assert JSONRPCErrorCode.METHOD_NOT_FOUND == -32601
        assert JSONRPCErrorCode.INVALID_PARAMS == -32602
        assert JSONRPCErrorCode.INTERNAL_ERROR == -32603
