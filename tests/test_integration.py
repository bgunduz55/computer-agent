"""
Integration Tests for Intelligent Command System

Tests the complete integration of all components working together.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock

from src.features.command_processing.capability_system import get_capability_manager
from src.features.command_processing.error_recovery import get_error_recovery_manager
from src.features.command_processing.command_security import get_security_validator
from src.features.command_processing.intelligent_command_processor import IntelligentCommandProcessor

class TestIntelligentCommandIntegration:
    """Test complete intelligent command system integration"""
    
    @pytest.fixture
    def initialized_system(self):
        """Initialize the complete system"""
        async def _init_system():
            # Get managers
            capability_manager = await get_capability_manager()
            await capability_manager.initialize()
            error_recovery_manager = get_error_recovery_manager()
            security_validator = get_security_validator()
            
            # Mock AI manager
            mock_ai_manager = Mock()
            mock_ai_manager.is_initialized.return_value = True
            
            # Create intelligent command processor
            processor = IntelligentCommandProcessor(mock_ai_manager, capability_manager)
            await processor.initialize()
            
            return {
                'capability_manager': capability_manager,
                'error_recovery_manager': error_recovery_manager,
                'security_validator': security_validator,
                'processor': processor
            }
        
        # Return a coroutine that can be awaited in tests
        return _init_system()
    
    @pytest.mark.asyncio
    async def test_system_info_command(self, initialized_system):
        """Test system information command execution"""
        system = await initialized_system
        
        # Test system info capability
        result = await system['capability_manager'].execute_capability(
            "system_info",
            {"info_type": "all"},
            {}
        )
        
        assert result['success'] is True
        assert 'data' in result
        assert 'platform' in result['data']
    
    @pytest.mark.asyncio
    async def test_file_operations_command(self, initialized_system):
        """Test file operations command execution"""
        system = await initialized_system
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test file creation
            result = await system['capability_manager'].execute_capability(
                "file_create_text",
                {
                    "file_path": os.path.join(temp_dir, "test.txt"),
                    "content": "Test content"
                },
                {}
            )
            
            assert result['success'] is True
            
            # Test file listing
            list_result = await system['capability_manager'].execute_capability(
                "file_list",
                {"directory": temp_dir},
                {}
            )
            
            assert list_result['success'] is True
            assert 'data' in list_result
            assert len(list_result['data']) > 0
    
    @pytest.mark.asyncio
    async def test_security_validation(self, initialized_system):
        """Test security validation integration"""
        system = await initialized_system
        
        # Create security context
        from src.features.command_processing.command_security import SecurityContext, SecurityLevel
        context = SecurityContext(
            user_id="test_user",
            session_id="test_session",
            ip_address="127.0.0.1",
            user_agent="test_agent",
            permissions={"file_read", "web_access"},
            security_level=SecurityLevel.MEDIUM
        )
        
        # Test safe command
        safe_result = await system['security_validator'].validate_command(
            "echo hello", context
        )
        assert safe_result.is_safe is True
        
        # Test dangerous command
        dangerous_result = await system['security_validator'].validate_command(
            "rm -rf /", context
        )
        assert dangerous_result.is_safe is False
    
    @pytest.mark.asyncio
    async def test_error_recovery_integration(self, initialized_system):
        """Test error recovery integration"""
        system = await initialized_system
        
        # Create execution step
        from src.features.command_processing.error_recovery import ExecutionStep, ExecutionContext
        step = ExecutionStep(
            step_id="test_step",
            name="Test Step",
            capability="test_capability",
            parameters={},
            dependencies=[]
        )
        
        context = ExecutionContext(
            command_id="test_command",
            steps=[step],
            variables={},
            rollback_stack=[],
            recovery_actions=[]
        )
        
        # Test error handling
        test_error = Exception("Test error")
        result = await system['error_recovery_manager'].handle_execution_error(
            step, test_error, context
        )
        
        assert 'success' in result
        assert 'error' in result or 'action' in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
