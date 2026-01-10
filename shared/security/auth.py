import secrets
import hashlib
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel


class TokenInfo(BaseModel):
    token: str
    slave_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    scopes: list[str] = []


class AuthManager:
    def __init__(self):
        self._tokens: dict[str, TokenInfo] = {}
    
    def generate_token(
        self, 
        slave_id: str, 
        scopes: list[str] = None,
        expires_in_hours: Optional[int] = None
    ) -> str:
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        self._tokens[token_hash] = TokenInfo(
            token=token_hash,
            slave_id=slave_id,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            scopes=scopes or []
        )
        
        return raw_token
    
    def validate_token(self, token: str) -> Optional[TokenInfo]:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        token_info = self._tokens.get(token_hash)
        
        if not token_info:
            return None
        
        if token_info.expires_at and datetime.utcnow() > token_info.expires_at:
            del self._tokens[token_hash]
            return None
        
        return token_info
    
    def revoke_token(self, token: str) -> bool:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if token_hash in self._tokens:
            del self._tokens[token_hash]
            return True
        return False
    
    def has_scope(self, token_info: TokenInfo, required_scope: str) -> bool:
        if not token_info.scopes:
            return True
        return required_scope in token_info.scopes or "*" in token_info.scopes
