"""
Dynamic capability definitions for the intelligent command system.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum


class CapabilityType(Enum):
    """Types of dynamic capabilities"""
    TERMINAL = "terminal"
    AI_GENERATED = "ai_generated"
    PLUGIN = "plugin"


@dataclass
class DynamicCapability:
    """Represents a dynamically created capability"""
    
    name: str
    description: str
    capability_type: CapabilityType
    parameters: Dict[str, Any]
    command_template: Optional[str] = None
    ai_prompt: Optional[str] = None
    plugin_id: Optional[str] = None
    security_level: str = "medium"  # low, medium, high
    requires_confirmation: bool = False
    timeout_seconds: int = 30
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "capability_type": self.capability_type.value,
            "parameters": self.parameters,
            "command_template": self.command_template,
            "ai_prompt": self.ai_prompt,
            "plugin_id": self.plugin_id,
            "security_level": self.security_level,
            "requires_confirmation": self.requires_confirmation,
            "timeout_seconds": self.timeout_seconds,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DynamicCapability':
        """Create from dictionary"""
        return cls(
            name=data["name"],
            description=data["description"],
            capability_type=CapabilityType(data["capability_type"]),
            parameters=data["parameters"],
            command_template=data.get("command_template"),
            ai_prompt=data.get("ai_prompt"),
            plugin_id=data.get("plugin_id"),
            security_level=data.get("security_level", "medium"),
            requires_confirmation=data.get("requires_confirmation", False),
            timeout_seconds=data.get("timeout_seconds", 30),
            tags=data.get("tags", [])
        )
