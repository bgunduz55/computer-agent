"""
Security Manager for JARVIS Computer Assistant
Handles security, authentication, encryption, and threat detection
"""

import asyncio
import logging
import hashlib
import secrets
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
import re
import time


@dataclass
class SecurityEvent:
    """Security event data"""
    event_type: str
    severity: str  # low, medium, high, critical
    message: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class AuthToken:
    """Authentication token data"""
    token: str
    user_id: str
    expires_at: datetime
    permissions: List[str]
    created_at: datetime


@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    max_login_attempts: int = 3
    lockout_duration_minutes: int = 15
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    token_expiry_hours: int = 24
    enable_encryption: bool = True
    enable_audit_logging: bool = True
    enable_threat_detection: bool = True
    max_command_length: int = 1000
    allowed_command_patterns: List[str] = None
    blocked_command_patterns: List[str] = None
    
    def __post_init__(self):
        if self.allowed_command_patterns is None:
            self.allowed_command_patterns = []
        if self.blocked_command_patterns is None:
            self.blocked_command_patterns = [
                r'rm\s+-rf\s+/',  # Dangerous delete commands
                r'format\s+[a-zA-Z]:',  # Windows format commands
                r'del\s+/[qsf]',  # Windows delete commands
                r'reg\s+delete',  # Registry deletions
                r'shutdown\s+',  # Shutdown commands
                r'reboot',  # Reboot commands
                r'halt',  # System halt
                r'mkfs\.',  # Format filesystem
                r'dd\s+if=.*of=/dev/',  # Dangerous dd commands
            ]


class CryptoManager:
    """Handles encryption and cryptographic operations"""
    
    def __init__(self, key: bytes = None):
        self.logger = logging.getLogger(__name__)
        if key:
            self.key = key
        else:
            self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt string data"""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode(), salt)
            return hashed.decode()
        except Exception as e:
            self.logger.error(f"Password hashing failed: {e}")
            raise
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception as e:
            self.logger.error(f"Password verification failed: {e}")
            return False
    
    def generate_token(self, user_id: str, permissions: List[str], 
                      expiry_hours: int = 24) -> str:
        """Generate JWT token"""
        try:
            payload = {
                'user_id': user_id,
                'permissions': permissions,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(hours=expiry_hours)
            }
            token = jwt.encode(payload, self.key, algorithm='HS256')
            return token
        except Exception as e:
            self.logger.error(f"Token generation failed: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Token verification failed: {e}")
            return None


class ThreatDetector:
    """Detects security threats and suspicious activities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._failed_attempts: Dict[str, List[datetime]] = {}
        self._command_history: List[str] = []
        self._suspicious_patterns = [
            r'\.exe\s+.*--hidden',  # Hidden executables
            r'powershell.*-enc\s+',  # Encoded PowerShell
            r'cmd.*\/c.*&',  # Command chaining
            r'curl.*\|\s*bash',  # Pipe to bash
            r'wget.*\|\s*sh',  # Pipe to shell
            r'nc\s+.*-e\s+',  # Netcat with execute
            r'python.*-c.*exec',  # Python exec
            r'eval\s*\(',  # Eval functions
            r'exec\s*\(',  # Exec functions
        ]
    
    def analyze_command(self, command: str, user_id: str = "unknown") -> List[SecurityEvent]:
        """Analyze command for threats"""
        events = []
        
        try:
            # Check command length
            if len(command) > 1000:
                events.append(SecurityEvent(
                    event_type="command_length_exceeded",
                    severity="medium",
                    message=f"Command length ({len(command)}) exceeds limit",
                    source="threat_detector",
                    timestamp=datetime.now(),
                    metadata={"command_length": len(command), "user_id": user_id}
                ))
            
            # Check for suspicious patterns
            for pattern in self._suspicious_patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    events.append(SecurityEvent(
                        event_type="suspicious_command_pattern",
                        severity="high",
                        message=f"Suspicious pattern detected: {pattern}",
                        source="threat_detector",
                        timestamp=datetime.now(),
                        metadata={"pattern": pattern, "command": command[:100], "user_id": user_id}
                    ))
            
            # Check for rapid command execution
            self._command_history.append(command)
            if len(self._command_history) > 100:
                self._command_history = self._command_history[-100:]
            
            # Check for repeated failed attempts
            recent_commands = self._command_history[-10:]
            if len(recent_commands) >= 5:
                unique_commands = set(recent_commands)
                if len(unique_commands) == 1:  # Same command repeated
                    events.append(SecurityEvent(
                        event_type="command_repetition",
                        severity="medium",
                        message="Same command repeated multiple times",
                        source="threat_detector",
                        timestamp=datetime.now(),
                        metadata={"command": command[:100], "count": len(recent_commands), "user_id": user_id}
                    ))
            
        except Exception as e:
            self.logger.error(f"Error analyzing command: {e}")
        
        return events
    
    def record_failed_attempt(self, user_id: str, attempt_type: str = "login") -> bool:
        """Record failed attempt and check if user should be locked out"""
        try:
            now = datetime.now()
            
            if user_id not in self._failed_attempts:
                self._failed_attempts[user_id] = []
            
            # Add current attempt
            self._failed_attempts[user_id].append(now)
            
            # Clean old attempts (older than 1 hour)
            cutoff = now - timedelta(hours=1)
            self._failed_attempts[user_id] = [
                attempt for attempt in self._failed_attempts[user_id]
                if attempt > cutoff
            ]
            
            # Check if lockout threshold reached
            return len(self._failed_attempts[user_id]) >= 3
            
        except Exception as e:
            self.logger.error(f"Error recording failed attempt: {e}")
            return False
    
    def is_user_locked_out(self, user_id: str, lockout_duration_minutes: int = 15) -> bool:
        """Check if user is currently locked out"""
        try:
            if user_id not in self._failed_attempts:
                return False
            
            if len(self._failed_attempts[user_id]) < 3:
                return False
            
            # Check if lockout period has expired
            latest_attempt = max(self._failed_attempts[user_id])
            lockout_expires = latest_attempt + timedelta(minutes=lockout_duration_minutes)
            
            return datetime.now() < lockout_expires
            
        except Exception as e:
            self.logger.error(f"Error checking lockout status: {e}")
            return False


class SecurityManager:
    """
    Main security management system
    Handles authentication, encryption, threat detection, and security policies
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.crypto_manager = CryptoManager()
        self.threat_detector = ThreatDetector()
        self.policy = SecurityPolicy()
        self._security_events: List[SecurityEvent] = []
        self._active_tokens: Dict[str, AuthToken] = {}
        self._audit_log: List[Dict[str, Any]] = []
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._running = False
        
    async def initialize(self) -> bool:
        """Initialize security manager"""
        try:
            self.logger.info("Initializing security manager")
            
            # Load security configuration
            await self._load_security_config()
            
            # Start security monitoring
            await self._start_monitoring()
            
            self._running = True
            self.logger.info("Security manager initialized successfully")
            
            # Log security initialization
            await self._log_security_event("security_manager_initialized", "info", 
                                          "Security manager started successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize security manager: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown security manager"""
        try:
            self.logger.info("Shutting down security manager")
            
            self._running = False
            
            # Log security shutdown
            await self._log_security_event("security_manager_shutdown", "info", 
                                          "Security manager stopped")
            
            # Clear sensitive data
            self._active_tokens.clear()
            
            self.logger.info("Security manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during security manager shutdown: {e}")
    
    async def _load_security_config(self) -> None:
        """Load security configuration"""
        # In a real implementation, this would load from secure configuration
        self.logger.info("Loading security configuration")
    
    async def _start_monitoring(self) -> None:
        """Start security monitoring"""
        self.logger.info("Security monitoring started")
    
    async def validate_command(self, command: str, user_id: str = "system") -> bool:
        """Validate command for security threats"""
        try:
            # Check if user is locked out
            if self.threat_detector.is_user_locked_out(user_id, self.policy.lockout_duration_minutes):
                await self._log_security_event("command_blocked_lockout", "warning", 
                                              f"Command blocked - user {user_id} is locked out")
                return False
            
            # Analyze command for threats
            threats = self.threat_detector.analyze_command(command, user_id)
            
            if threats:
                # Log security events
                for threat in threats:
                    self._security_events.append(threat)
                    await self._log_security_event(threat.event_type, threat.severity, threat.message)
                
                # Block high/critical severity threats
                critical_threats = [t for t in threats if t.severity in ['high', 'critical']]
                if critical_threats:
                    await self._log_security_event("command_blocked_threat", "warning", 
                                                  f"Command blocked due to {len(critical_threats)} threat(s)")
                    return False
            
            # Check against security policy
            if not self._check_command_policy(command):
                await self._log_security_event("command_blocked_policy", "warning", 
                                              "Command blocked by security policy")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating command: {e}")
            return False
    
    def _check_command_policy(self, command: str) -> bool:
        """Check command against security policy"""
        try:
            # Check command length
            if len(command) > self.policy.max_command_length:
                return False
            
            # Check blocked patterns
            for pattern in self.policy.blocked_command_patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    return False
            
            # Check allowed patterns (if any specified)
            if self.policy.allowed_command_patterns:
                allowed = False
                for pattern in self.policy.allowed_command_patterns:
                    if re.search(pattern, command, re.IGNORECASE):
                        allowed = True
                        break
                if not allowed:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking command policy: {e}")
            return False
    
    async def authenticate_user(self, user_id: str, password: str) -> Optional[AuthToken]:
        """Authenticate user and return token"""
        try:
            # Check if user is locked out
            if self.threat_detector.is_user_locked_out(user_id, self.policy.lockout_duration_minutes):
                await self._log_security_event("authentication_blocked_lockout", "warning", 
                                              f"Authentication blocked - user {user_id} is locked out")
                return None
            
            # In a real implementation, this would check against a user database
            # For now, we'll accept any non-empty password
            if not password:
                self.threat_detector.record_failed_attempt(user_id, "login")
                await self._log_security_event("authentication_failed", "warning", 
                                              f"Authentication failed for user {user_id}")
                return None
            
            # Generate token
            permissions = ["basic_access", "voice_commands", "system_info"]
            token_str = self.crypto_manager.generate_token(user_id, permissions, self.policy.token_expiry_hours)
            
            token = AuthToken(
                token=token_str,
                user_id=user_id,
                expires_at=datetime.now() + timedelta(hours=self.policy.token_expiry_hours),
                permissions=permissions,
                created_at=datetime.now()
            )
            
            self._active_tokens[token_str] = token
            
            await self._log_security_event("authentication_success", "info", 
                                          f"User {user_id} authenticated successfully")
            
            return token
            
        except Exception as e:
            self.logger.error(f"Error authenticating user: {e}")
            self.threat_detector.record_failed_attempt(user_id, "login")
            return None
    
    async def validate_token(self, token_str: str) -> Optional[AuthToken]:
        """Validate authentication token"""
        try:
            if token_str not in self._active_tokens:
                return None
            
            token = self._active_tokens[token_str]
            
            # Check if token has expired
            if datetime.now() > token.expires_at:
                del self._active_tokens[token_str]
                await self._log_security_event("token_expired", "info", 
                                              f"Token expired for user {token.user_id}")
                return None
            
            # Verify token signature
            payload = self.crypto_manager.verify_token(token_str)
            if not payload:
                del self._active_tokens[token_str]
                await self._log_security_event("token_invalid", "warning", 
                                              f"Invalid token for user {token.user_id}")
                return None
            
            return token
            
        except Exception as e:
            self.logger.error(f"Error validating token: {e}")
            return None
    
    async def revoke_token(self, token_str: str) -> bool:
        """Revoke authentication token"""
        try:
            if token_str in self._active_tokens:
                token = self._active_tokens[token_str]
                del self._active_tokens[token_str]
                
                await self._log_security_event("token_revoked", "info", 
                                              f"Token revoked for user {token.user_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error revoking token: {e}")
            return False
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if self.policy.enable_encryption:
            return self.crypto_manager.encrypt_data(data)
        return data
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if self.policy.enable_encryption:
            return self.crypto_manager.decrypt_data(encrypted_data)
        return encrypted_data
    
    async def _log_security_event(self, event_type: str, severity: str, message: str, 
                                 metadata: Dict[str, Any] = None) -> None:
        """Log security event"""
        try:
            if not self.policy.enable_audit_logging:
                return
            
            event = {
                "event_type": event_type,
                "severity": severity,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }
            
            self._audit_log.append(event)
            
            # Keep only last 1000 events
            if len(self._audit_log) > 1000:
                self._audit_log = self._audit_log[-1000:]
            
            # Log to standard logger based on severity
            if severity == "critical":
                self.logger.critical(f"SECURITY: {message}")
            elif severity == "high":
                self.logger.error(f"SECURITY: {message}")
            elif severity == "warning":
                self.logger.warning(f"SECURITY: {message}")
            else:
                self.logger.info(f"SECURITY: {message}")
            
            # Emit event
            await self._emit_security_event(event)
            
        except Exception as e:
            self.logger.error(f"Error logging security event: {e}")
    
    async def _emit_security_event(self, event: Dict[str, Any]) -> None:
        """Emit security event to handlers"""
        event_type = event.get("event_type", "unknown")
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    self.logger.error(f"Error in security event handler: {e}")
    
    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """Add security event handler"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary"""
        try:
            recent_events = [e for e in self._security_events 
                           if (datetime.now() - e.timestamp).total_seconds() < 3600]  # Last hour
            
            return {
                "status": "running" if self._running else "stopped",
                "active_tokens": len(self._active_tokens),
                "total_security_events": len(self._security_events),
                "recent_security_events": len(recent_events),
                "audit_log_entries": len(self._audit_log),
                "threat_detection_enabled": self.policy.enable_threat_detection,
                "encryption_enabled": self.policy.enable_encryption,
                "audit_logging_enabled": self.policy.enable_audit_logging,
                "policy": {
                    "max_login_attempts": self.policy.max_login_attempts,
                    "lockout_duration_minutes": self.policy.lockout_duration_minutes,
                    "token_expiry_hours": self.policy.token_expiry_hours,
                    "max_command_length": self.policy.max_command_length
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting security summary: {e}")
            return {"status": "error", "error": str(e)}


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get global security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


async def cleanup_security_manager() -> None:
    """Cleanup global security manager"""
    global _security_manager
    if _security_manager is not None:
        await _security_manager.shutdown()
        _security_manager = None
