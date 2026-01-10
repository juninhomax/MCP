import pytest
from shared.security.auth import AuthManager
from datetime import datetime, timedelta


class TestAuthManager:
    def setup_method(self):
        self.auth_manager = AuthManager()
    
    def test_generate_token(self):
        token = self.auth_manager.generate_token(
            slave_id="test-slave",
            scopes=["read", "write"]
        )
        assert token is not None
        assert len(token) > 0
    
    def test_validate_token(self):
        token = self.auth_manager.generate_token(
            slave_id="test-slave",
            scopes=["read"]
        )
        
        token_info = self.auth_manager.validate_token(token)
        assert token_info is not None
        assert token_info.slave_id == "test-slave"
        assert "read" in token_info.scopes
    
    def test_validate_invalid_token(self):
        token_info = self.auth_manager.validate_token("invalid-token-12345")
        assert token_info is None
    
    def test_token_expiration(self):
        token = self.auth_manager.generate_token(
            slave_id="test-slave",
            expires_in_hours=-1
        )
        
        token_info = self.auth_manager.validate_token(token)
        assert token_info is None
    
    def test_revoke_token(self):
        token = self.auth_manager.generate_token(slave_id="test-slave")
        
        token_info = self.auth_manager.validate_token(token)
        assert token_info is not None
        
        revoked = self.auth_manager.revoke_token(token)
        assert revoked is True
        
        token_info = self.auth_manager.validate_token(token)
        assert token_info is None
    
    def test_has_scope(self):
        token = self.auth_manager.generate_token(
            slave_id="test-slave",
            scopes=["read", "write"]
        )
        
        token_info = self.auth_manager.validate_token(token)
        assert self.auth_manager.has_scope(token_info, "read") is True
        assert self.auth_manager.has_scope(token_info, "write") is True
        assert self.auth_manager.has_scope(token_info, "admin") is False
    
    def test_wildcard_scope(self):
        token = self.auth_manager.generate_token(
            slave_id="test-slave",
            scopes=["*"]
        )
        
        token_info = self.auth_manager.validate_token(token)
        assert self.auth_manager.has_scope(token_info, "anything") is True
