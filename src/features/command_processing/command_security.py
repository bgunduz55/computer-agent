"""
Command Security Validation System

Implements comprehensive security validation for intelligent commands,
including permission checking, input sanitization, and threat detection.
"""

import re
import logging
import hashlib
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for commands"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Types of security threats"""
    INJECTION = "injection"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXPOSURE = "data_exposure"
    SYSTEM_DAMAGE = "system_damage"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALICIOUS_CODE = "malicious_code"

@dataclass
class SecurityRule:
    """A security validation rule"""
    name: str
    pattern: str
    threat_type: ThreatType
    severity: SecurityLevel
    description: str
    action: str  # "block", "warn", "require_confirmation"

@dataclass
class SecurityContext:
    """Security context for command validation"""
    user_id: str
    session_id: str
    ip_address: str
    user_agent: str
    permissions: Set[str]
    security_level: SecurityLevel
    trusted_mode: bool = False
    confirmation_required: bool = True

@dataclass
class ValidationResult:
    """Result of security validation"""
    is_safe: bool
    threat_level: SecurityLevel
    threats_detected: List[ThreatType]
    warnings: List[str]
    blocked_patterns: List[str]
    requires_confirmation: bool
    suggested_alternatives: List[str]

class CommandSecurityValidator:
    """Validates commands for security threats and compliance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_rules: List[SecurityRule] = []
        self.whitelist_patterns: Set[str] = set()
        self.blacklist_patterns: Set[str] = set()
        self.user_permissions: Dict[str, Set[str]] = {}
        self.session_history: Dict[str, List[Dict[str, Any]]] = {}
        
        self._initialize_security_rules()
        self._initialize_patterns()
    
    def _initialize_security_rules(self):
        """Initialize security validation rules"""
        # Command injection patterns
        self.security_rules.extend([
            SecurityRule(
                name="command_injection_semicolon",
                pattern=r'[;&|`$]',
                threat_type=ThreatType.INJECTION,
                severity=SecurityLevel.HIGH,
                description="Command injection via shell operators",
                action="block"
            ),
            SecurityRule(
                name="command_injection_pipes",
                pattern=r'\|[^|]',
                threat_type=ThreatType.INJECTION,
                severity=SecurityLevel.MEDIUM,
                description="Command chaining via pipes",
                action="require_confirmation"
            ),
            SecurityRule(
                name="command_injection_redirects",
                pattern=r'[><]',
                threat_type=ThreatType.INJECTION,
                severity=SecurityLevel.MEDIUM,
                description="File redirection operators",
                action="require_confirmation"
            )
        ])
        
        # Privilege escalation patterns
        self.security_rules.extend([
            SecurityRule(
                name="privilege_escalation_sudo",
                pattern=r'\bsudo\b',
                threat_type=ThreatType.PRIVILEGE_ESCALATION,
                severity=SecurityLevel.CRITICAL,
                description="Sudo command execution",
                action="block"
            ),
            SecurityRule(
                name="privilege_escalation_su",
                pattern=r'\bsu\b',
                threat_type=ThreatType.PRIVILEGE_ESCALATION,
                severity=SecurityLevel.CRITICAL,
                description="Switch user command",
                action="block"
            ),
            SecurityRule(
                name="privilege_escalation_runas",
                pattern=r'\brunas\b',
                threat_type=ThreatType.PRIVILEGE_ESCALATION,
                severity=SecurityLevel.CRITICAL,
                description="Run as different user",
                action="block"
            )
        ])
        
        # System damage patterns
        self.security_rules.extend([
            SecurityRule(
                name="system_damage_rm",
                pattern=r'\brm\s+-rf\b',
                threat_type=ThreatType.SYSTEM_DAMAGE,
                severity=SecurityLevel.CRITICAL,
                description="Recursive file deletion",
                action="block"
            ),
            SecurityRule(
                name="system_damage_format",
                pattern=r'\bformat\b',
                threat_type=ThreatType.SYSTEM_DAMAGE,
                severity=SecurityLevel.CRITICAL,
                description="Disk formatting command",
                action="block"
            ),
            SecurityRule(
                name="system_damage_dd",
                pattern=r'\bdd\s+if=',
                threat_type=ThreatType.SYSTEM_DAMAGE,
                severity=SecurityLevel.CRITICAL,
                description="Direct disk access",
                action="block"
            ),
            SecurityRule(
                name="system_damage_shutdown",
                pattern=r'\b(shutdown|reboot|halt|poweroff)\b',
                threat_type=ThreatType.SYSTEM_DAMAGE,
                severity=SecurityLevel.HIGH,
                description="System shutdown commands",
                action="require_confirmation"
            )
        ])
        
        # Data exposure patterns
        self.security_rules.extend([
            SecurityRule(
                name="data_exposure_passwords",
                pattern=r'\b(password|passwd|pwd)\b',
                threat_type=ThreatType.DATA_EXPOSURE,
                severity=SecurityLevel.MEDIUM,
                description="Password-related commands",
                action="require_confirmation"
            ),
            SecurityRule(
                name="data_exposure_keys",
                pattern=r'\b(ssh-key|private-key|secret)\b',
                threat_type=ThreatType.DATA_EXPOSURE,
                severity=SecurityLevel.HIGH,
                description="Private key access",
                action="require_confirmation"
            ),
            SecurityRule(
                name="data_exposure_history",
                pattern=r'\b(history|bash_history)\b',
                threat_type=ThreatType.DATA_EXPOSURE,
                severity=SecurityLevel.MEDIUM,
                description="Command history access",
                action="require_confirmation"
            )
        ])
        
        # Malicious code patterns
        self.security_rules.extend([
            SecurityRule(
                name="malicious_code_eval",
                pattern=r'\beval\s*\(',
                threat_type=ThreatType.MALICIOUS_CODE,
                severity=SecurityLevel.HIGH,
                description="Code evaluation",
                action="block"
            ),
            SecurityRule(
                name="malicious_code_exec",
                pattern=r'\bexec\s*\(',
                threat_type=ThreatType.MALICIOUS_CODE,
                severity=SecurityLevel.HIGH,
                description="Code execution",
                action="block"
            ),
            SecurityRule(
                name="malicious_code_import",
                pattern=r'\bimport\s+os\b',
                threat_type=ThreatType.MALICIOUS_CODE,
                severity=SecurityLevel.MEDIUM,
                description="OS module import",
                action="require_confirmation"
            )
        ])
    
    def _initialize_patterns(self):
        """Initialize whitelist and blacklist patterns"""
        # Whitelist patterns (always allowed)
        self.whitelist_patterns.update([
            r'^echo\s+',
            r'^date\s*$',
            r'^whoami\s*$',
            r'^pwd\s*$',
            r'^ls\s+',
            r'^cat\s+',
            r'^grep\s+',
            r'^find\s+',
            r'^ps\s+',
            r'^top\s*$',
            r'^df\s*$',
            r'^free\s*$',
            r'^uname\s*$'
        ])
        
        # Blacklist patterns (always blocked)
        self.blacklist_patterns.update([
            r'rm\s+-rf\s+/',
            r'format\s+[c-z]:',
            r'dd\s+if=/dev/',
            r'mkfs\s+',
            r'fdisk\s+',
            r'parted\s+',
            r'chmod\s+777\s+/',
            r'chown\s+root\s+/',
            r'passwd\s+',
            r'useradd\s+',
            r'userdel\s+',
            r'groupadd\s+',
            r'groupdel\s+'
        ])
    
    async def validate_command(
        self, 
        command: str, 
        context: SecurityContext
    ) -> ValidationResult:
        """Validate a command for security threats"""
        try:
            threats_detected = []
            warnings = []
            blocked_patterns = []
            requires_confirmation = False
            suggested_alternatives = []
            
            # Check whitelist first
            if self._is_whitelisted(command):
                return ValidationResult(
                    is_safe=True,
                    threat_level=SecurityLevel.LOW,
                    threats_detected=[],
                    warnings=[],
                    blocked_patterns=[],
                    requires_confirmation=False,
                    suggested_alternatives=[]
                )
            
            # Check blacklist
            if self._is_blacklisted(command):
                return ValidationResult(
                    is_safe=False,
                    threat_level=SecurityLevel.CRITICAL,
                    threats_detected=[ThreatType.SYSTEM_DAMAGE],
                    warnings=["Command is blacklisted"],
                    blocked_patterns=[command],
                    requires_confirmation=False,
                    suggested_alternatives=[]
                )
            
            # Apply security rules
            for rule in self.security_rules:
                if re.search(rule.pattern, command, re.IGNORECASE):
                    threats_detected.append(rule.threat_type)
                    blocked_patterns.append(rule.pattern)
                    
                    if rule.action == "block":
                        return ValidationResult(
                            is_safe=False,
                            threat_level=rule.severity,
                            threats_detected=threats_detected,
                            warnings=[rule.description],
                            blocked_patterns=blocked_patterns,
                            requires_confirmation=False,
                            suggested_alternatives=[]
                        )
                    elif rule.action == "require_confirmation":
                        requires_confirmation = True
                        warnings.append(rule.description)
                    elif rule.action == "warn":
                        warnings.append(rule.description)
            
            # Check user permissions
            permission_check = await self._check_permissions(command, context)
            if not permission_check["allowed"]:
                return ValidationResult(
                    is_safe=False,
                    threat_level=SecurityLevel.HIGH,
                    threats_detected=[ThreatType.UNAUTHORIZED_ACCESS],
                    warnings=[permission_check["reason"]],
                    blocked_patterns=[],
                    requires_confirmation=False,
                    suggested_alternatives=permission_check.get("alternatives", [])
                )
            
            # Check session history for suspicious patterns
            history_check = await self._check_session_history(command, context)
            if not history_check["safe"]:
                warnings.extend(history_check["warnings"])
                requires_confirmation = True
            
            # Determine overall threat level
            threat_level = self._determine_threat_level(threats_detected)
            
            # Generate suggested alternatives
            suggested_alternatives = await self._generate_alternatives(command, threats_detected)
            
            return ValidationResult(
                is_safe=threat_level in [SecurityLevel.LOW, SecurityLevel.MEDIUM],
                threat_level=threat_level,
                threats_detected=threats_detected,
                warnings=warnings,
                blocked_patterns=blocked_patterns,
                requires_confirmation=requires_confirmation or context.confirmation_required,
                suggested_alternatives=suggested_alternatives
            )
            
        except Exception as e:
            self.logger.error(f"Error validating command: {e}")
            return ValidationResult(
                is_safe=False,
                threat_level=SecurityLevel.CRITICAL,
                threats_detected=[ThreatType.MALICIOUS_CODE],
                warnings=[f"Validation error: {e}"],
                blocked_patterns=[],
                requires_confirmation=False,
                suggested_alternatives=[]
            )
    
    def _is_whitelisted(self, command: str) -> bool:
        """Check if command is whitelisted"""
        for pattern in self.whitelist_patterns:
            if re.match(pattern, command, re.IGNORECASE):
                return True
        return False
    
    def _is_blacklisted(self, command: str) -> bool:
        """Check if command is blacklisted"""
        for pattern in self.blacklist_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False
    
    async def _check_permissions(self, command: str, context: SecurityContext) -> Dict[str, Any]:
        """Check if user has permission to execute command"""
        try:
            # Extract capability from command (simplified)
            capability = self._extract_capability(command)
            
            if not capability:
                return {"allowed": True, "reason": "No capability restrictions"}
            
            # Check if user has permission for this capability
            required_permissions = self._get_required_permissions(capability)
            
            if not required_permissions:
                return {"allowed": True, "reason": "No specific permissions required"}
            
            # Check if user has all required permissions
            missing_permissions = required_permissions - context.permissions
            
            if missing_permissions:
                return {
                    "allowed": False,
                    "reason": f"Missing permissions: {', '.join(missing_permissions)}",
                    "alternatives": self._get_alternative_capabilities(capability)
                }
            
            return {"allowed": True, "reason": "User has required permissions"}
            
        except Exception as e:
            self.logger.error(f"Error checking permissions: {e}")
            return {"allowed": False, "reason": f"Permission check failed: {e}"}
    
    def _extract_capability(self, command: str) -> Optional[str]:
        """Extract capability name from command"""
        # This is a simplified extraction - in practice, this would be more sophisticated
        command_parts = command.split()
        if command_parts:
            return command_parts[0]
        return None
    
    def _get_required_permissions(self, capability: str) -> Set[str]:
        """Get required permissions for a capability"""
        permission_map = {
            "system_shutdown": {"system_control"},
            "system_restart": {"system_control"},
            "volume_control": {"media_control"},
            "brightness_control": {"display_control"},
            "file_create": {"file_write"},
            "file_delete": {"file_delete"},
            "app_open": {"application_control"},
            "web_search": {"web_access"},
            "terminal_command": {"terminal_access"}
        }
        
        return permission_map.get(capability, set())
    
    def _get_alternative_capabilities(self, capability: str) -> List[str]:
        """Get alternative capabilities for a restricted capability"""
        alternatives = {
            "system_shutdown": ["system_info"],
            "file_delete": ["file_list", "file_read"],
            "terminal_command": ["web_search", "file_list"]
        }
        
        return alternatives.get(capability, [])
    
    async def _check_session_history(self, command: str, context: SecurityContext) -> Dict[str, Any]:
        """Check session history for suspicious patterns"""
        try:
            session_commands = self.session_history.get(context.session_id, [])
            
            # Check for repeated failed attempts
            recent_failures = [
                cmd for cmd in session_commands[-10:] 
                if cmd.get("success", False) is False
            ]
            
            if len(recent_failures) >= 5:
                return {
                    "safe": False,
                    "warnings": ["Multiple recent command failures detected"]
                }
            
            # Check for suspicious command patterns
            suspicious_patterns = [
                "rm -rf", "format", "dd if=", "sudo", "su -"
            ]
            
            for pattern in suspicious_patterns:
                if pattern in command and any(pattern in cmd.get("command", "") for cmd in session_commands[-5:]):
                    return {
                        "safe": False,
                        "warnings": [f"Repeated suspicious pattern detected: {pattern}"]
                    }
            
            return {"safe": True, "warnings": []}
            
        except Exception as e:
            self.logger.error(f"Error checking session history: {e}")
            return {"safe": True, "warnings": []}
    
    def _determine_threat_level(self, threats_detected: List[ThreatType]) -> SecurityLevel:
        """Determine overall threat level based on detected threats"""
        if not threats_detected:
            return SecurityLevel.LOW
        
        # Check for critical threats
        critical_threats = [
            ThreatType.PRIVILEGE_ESCALATION,
            ThreatType.SYSTEM_DAMAGE
        ]
        
        if any(threat in critical_threats for threat in threats_detected):
            return SecurityLevel.CRITICAL
        
        # Check for high threats
        high_threats = [
            ThreatType.INJECTION,
            ThreatType.DATA_EXPOSURE
        ]
        
        if any(threat in high_threats for threat in threats_detected):
            return SecurityLevel.HIGH
        
        return SecurityLevel.MEDIUM
    
    async def _generate_alternatives(self, command: str, threats_detected: List[ThreatType]) -> List[str]:
        """Generate safer alternative commands"""
        alternatives = []
        
        # Generate alternatives based on threat types
        for threat in threats_detected:
            if threat == ThreatType.INJECTION:
                # Suggest safer alternatives for injection-prone commands
                if "rm -rf" in command:
                    alternatives.append("rm -i")  # Interactive removal
                elif "|" in command:
                    alternatives.append(command.replace("|", " | "))  # Add spaces for clarity
        
        return alternatives
    
    def add_security_rule(self, rule: SecurityRule):
        """Add a custom security rule"""
        self.security_rules.append(rule)
        self.logger.info(f"Added security rule: {rule.name}")
    
    def update_user_permissions(self, user_id: str, permissions: Set[str]):
        """Update user permissions"""
        self.user_permissions[user_id] = permissions
        self.logger.info(f"Updated permissions for user {user_id}: {permissions}")
    
    def log_command_execution(self, context: SecurityContext, command: str, success: bool):
        """Log command execution for session history"""
        if context.session_id not in self.session_history:
            self.session_history[context.session_id] = []
        
        self.session_history[context.session_id].append({
            "command": command,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "user_id": context.user_id
        })
        
        # Keep only last 100 commands per session
        if len(self.session_history[context.session_id]) > 100:
            self.session_history[context.session_id] = self.session_history[context.session_id][-100:]

# Global security validator instance
_security_validator: Optional[CommandSecurityValidator] = None

def get_security_validator() -> CommandSecurityValidator:
    """Get global security validator instance"""
    global _security_validator
    if _security_validator is None:
        _security_validator = CommandSecurityValidator()
    return _security_validator

# Export main classes
__all__ = [
    'CommandSecurityValidator',
    'SecurityLevel',
    'ThreatType',
    'SecurityRule',
    'SecurityContext',
    'ValidationResult',
    'get_security_validator'
]
