"""
Comprehensive Test Suite for Intelligent Command System

Tests all components of the intelligent command system including
capability executors, error recovery, security validation, and integration.
"""

import pytest
import asyncio
import tempfile
import os
import re
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Import system components
from src.features.command_processing.capability_system import (
    CapabilityManager, Capability, CapabilityType, ParameterInfo
)
from src.features.command_processing.capabilities.system_capabilities import (
    SystemShutdownExecutor, VolumeControlExecutor, 
    BrightnessControlExecutor, SystemInfoExecutor
)
from src.features.command_processing.capabilities.media_capabilities import (
    MusicPlaybackExecutor, VideoPlaybackExecutor, 
    BrowserControlExecutor, YouTubeControlExecutor
)
from src.features.command_processing.capabilities.productivity_capabilities import (
    TextEditorExecutor, FileManagerExecutor, 
    NoteTakingExecutor, ApplicationLauncherExecutor
)
from src.features.command_processing.capabilities.web_capabilities import (
    WebSearchExecutor, WebNavigationExecutor, 
    DataExtractionExecutor, FormAutomationExecutor
)
from src.features.command_processing.terminal_capability_executor import (
    TerminalCapabilityExecutor, TerminalExecutionResult
)
from src.features.command_processing.error_recovery import (
    ErrorRecoveryManager, RecoveryStrategy, ErrorSeverity,
    ExecutionStep, ExecutionContext
)
from src.features.command_processing.command_security import (
    CommandSecurityValidator, SecurityLevel, ThreatType,
    SecurityContext, ValidationResult
)

class TestSystemCapabilities:
    """Test system capability executors"""
    
    @pytest.fixture
    def system_executors(self):
        """Create system executor instances"""
        return {
            'shutdown': SystemShutdownExecutor(),
            'volume': VolumeControlExecutor(),
            'brightness': BrightnessControlExecutor(),
            'system_info': SystemInfoExecutor()
        }
    
    @pytest.mark.asyncio
    async def test_system_info_executor(self, system_executors):
        """Test system information retrieval"""
        executor = system_executors['system_info']
        
        # Test basic system info
        result = await executor.execute(
            parameters={'info_type': 'all'},
            context={}
        )
        
        assert result['success'] is True
        assert 'data' in result
        assert 'platform' in result['data']
        assert 'memory_total' in result['data']
    
    @pytest.mark.asyncio
    async def test_volume_control_executor(self, system_executors):
        """Test volume control operations"""
        executor = system_executors['volume']
        
        # Test volume control validation
        can_execute = executor.can_execute(
            parameters={'action': 'set', 'level': 50},
            context={}
        )
        assert can_execute is True
        
        # Test invalid level
        can_execute_invalid = executor.can_execute(
            parameters={'action': 'set', 'level': 150},
            context={}
        )
        assert can_execute_invalid is False
    
    @pytest.mark.asyncio
    async def test_brightness_control_executor(self, system_executors):
        """Test brightness control operations"""
        executor = system_executors['brightness']
        
        # Test brightness control validation
        can_execute = executor.can_execute(
            parameters={'action': 'set', 'level': 75},
            context={}
        )
        assert can_execute is True

class TestMediaCapabilities:
    """Test media capability executors"""
    
    @pytest.fixture
    def media_executors(self):
        """Create media executor instances"""
        return {
            'music': MusicPlaybackExecutor(),
            'video': VideoPlaybackExecutor(),
            'browser': BrowserControlExecutor(),
            'youtube': YouTubeControlExecutor()
        }
    
    @pytest.mark.asyncio
    async def test_music_playback_executor(self, media_executors):
        """Test music playback operations"""
        executor = media_executors['music']
        
        # Test action validation
        valid_actions = ['play', 'pause', 'stop', 'next', 'previous']
        for action in valid_actions:
            can_execute = executor.can_execute(
                parameters={'action': action},
                context={}
            )
            assert can_execute is True
        
        # Test invalid action
        can_execute_invalid = executor.can_execute(
            parameters={'action': 'invalid_action'},
            context={}
        )
        assert can_execute_invalid is False
    
    @pytest.mark.asyncio
    async def test_browser_control_executor(self, media_executors):
        """Test browser control operations"""
        executor = media_executors['browser']
        
        # Test URL opening validation
        can_execute = executor.can_execute(
            parameters={'action': 'open', 'url': 'https://example.com'},
            context={}
        )
        assert can_execute is True
        
        # Test missing URL
        can_execute_missing = executor.can_execute(
            parameters={'action': 'open'},
            context={}
        )
        assert can_execute_missing is False

class TestProductivityCapabilities:
    """Test productivity capability executors"""
    
    @pytest.fixture
    def productivity_executors(self):
        """Create productivity executor instances"""
        return {
            'text_editor': TextEditorExecutor(),
            'file_manager': FileManagerExecutor(),
            'note_taking': NoteTakingExecutor(),
            'app_launcher': ApplicationLauncherExecutor()
        }
    
    @pytest.mark.asyncio
    async def test_text_editor_executor(self, productivity_executors):
        """Test text editing operations"""
        executor = productivity_executors['text_editor']
        
        # Test file creation
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, 'test.txt')
            result = await executor.execute(
                parameters={
                    'action': 'create',
                    'file_path': file_path,
                    'content': 'Test content'
                },
                context={}
            )
            
            assert result['success'] is True
            assert os.path.exists(file_path)
            
            # Verify file content
            with open(file_path, 'r') as f:
                content = f.read()
            assert content == 'Test content'
    
    @pytest.mark.asyncio
    async def test_file_manager_executor(self, productivity_executors):
        """Test file management operations"""
        executor = productivity_executors['file_manager']
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test file listing
            result = await executor.execute(
                parameters={'action': 'list', 'path': temp_dir},
                context={}
            )
            
            assert result['success'] is True
            assert 'data' in result
            assert isinstance(result['data'], list)
    
    @pytest.mark.asyncio
    async def test_note_taking_executor(self, productivity_executors):
        """Test note-taking operations"""
        executor = productivity_executors['note_taking']
        
        # Test note creation
        result = await executor.execute(
            parameters={
                'action': 'create',
                'title': 'Test Note',
                'content': 'This is a test note',
                'category': 'test',
                'priority': 'medium'
            },
            context={}
        )
        
        assert result['success'] is True
        
        # Test note retrieval
        get_result = await executor.execute(
            parameters={'action': 'get', 'title': 'Test Note'},
            context={}
        )
        
        assert get_result['success'] is True
        assert 'data' in get_result
        assert get_result['data']['title'] == 'Test Note'

class TestWebCapabilities:
    """Test web capability executors"""
    
    @pytest.fixture
    def web_executors(self):
        """Create web executor instances"""
        return {
            'search': WebSearchExecutor(),
            'navigation': WebNavigationExecutor(),
            'data_extraction': DataExtractionExecutor(),
            'form_automation': FormAutomationExecutor()
        }
    
    @pytest.mark.asyncio
    async def test_web_search_executor(self, web_executors):
        """Test web search operations"""
        executor = web_executors['search']
        
        # Test search validation
        can_execute = executor.can_execute(
            parameters={'action': 'search', 'query': 'test query'},
            context={}
        )
        assert can_execute is True
        
        # Test image search validation
        can_execute_image = executor.can_execute(
            parameters={'action': 'image_search', 'query': 'test image'},
            context={}
        )
        assert can_execute_image is True
    
    @pytest.mark.asyncio
    async def test_web_navigation_executor(self, web_executors):
        """Test web navigation operations"""
        executor = web_executors['navigation']
        
        # Test URL opening validation
        can_execute = executor.can_execute(
            parameters={'action': 'open', 'url': 'https://example.com'},
            context={}
        )
        assert can_execute is True

class TestTerminalCapabilityExecutor:
    """Test terminal capability executor"""
    
    @pytest.fixture
    def terminal_executor(self):
        """Create terminal executor instance"""
        return TerminalCapabilityExecutor()
    
    @pytest.mark.asyncio
    async def test_command_security_validation(self, terminal_executor):
        """Test command security validation"""
        # Test dangerous command detection
        dangerous_commands = [
            'rm -rf /',
            'sudo rm -rf /',
            'format c:',
            'dd if=/dev/zero of=/dev/sda'
        ]
        
        for cmd in dangerous_commands:
            security_check = await terminal_executor._validate_command_security(
                cmd, {'user_confirmed': False}
            )
            assert security_check['safe'] is False
            assert 'dangerous' in security_check['reason'].lower()
    
    @pytest.mark.asyncio
    async def test_safe_pattern_usage(self, terminal_executor):
        """Test safe pattern usage detection"""
        # Test safe pipe usage
        safe_pipe = 'ps aux | grep python'
        is_safe = terminal_executor._is_safe_pattern_usage(safe_pipe, '|')
        assert is_safe is True
        
        # Test unsafe pipe usage
        unsafe_pipe = 'echo "test" | rm -rf /'
        is_safe = terminal_executor._is_safe_pattern_usage(unsafe_pipe, '|')
        assert is_safe is False

class TestErrorRecoveryManager:
    """Test error recovery and rollback system"""
    
    @pytest.fixture
    def recovery_manager(self):
        """Create error recovery manager instance"""
        return ErrorRecoveryManager()
    
    @pytest.fixture
    def sample_step(self):
        """Create sample execution step"""
        return ExecutionStep(
            step_id="test_step_1",
            name="Test Step",
            capability="test_capability",
            parameters={"param1": "value1"},
            dependencies=[]
        )
    
    @pytest.fixture
    def sample_context(self):
        """Create sample execution context"""
        return ExecutionContext(
            command_id="test_command_1",
            steps=[],
            variables={},
            rollback_stack=[],
            recovery_actions=[]
        )
    
    def test_error_severity_classification(self, recovery_manager, sample_step):
        """Test error severity classification"""
        # Test critical error
        critical_error = Exception("Permission denied")
        severity = recovery_manager._classify_error_severity(critical_error, sample_step)
        assert severity == ErrorSeverity.CRITICAL
        
        # Test high severity error
        high_error = Exception("Capability not found")
        severity = recovery_manager._classify_error_severity(high_error, sample_step)
        assert severity == ErrorSeverity.HIGH
        
        # Test medium severity error
        medium_error = Exception("Invalid parameter")
        severity = recovery_manager._classify_error_severity(medium_error, sample_step)
        assert severity == ErrorSeverity.MEDIUM
        
        # Test low severity error
        low_error = Exception("Temporary failure")
        severity = recovery_manager._classify_error_severity(low_error, sample_step)
        assert severity == ErrorSeverity.LOW
    
    def test_alternative_capability_finding(self, recovery_manager):
        """Test alternative capability finding"""
        # Test known alternatives
        alternatives = recovery_manager._find_alternative_capabilities("system_shutdown")
        assert "system_restart" in alternatives
        
        # Test unknown capability
        alternatives = recovery_manager._find_alternative_capabilities("unknown_capability")
        assert alternatives == []

class TestCommandSecurityValidator:
    """Test command security validation system"""
    
    @pytest.fixture
    def security_validator(self):
        """Create security validator instance"""
        return CommandSecurityValidator()
    
    @pytest.fixture
    def sample_context(self):
        """Create sample security context"""
        return SecurityContext(
            user_id="test_user",
            session_id="test_session",
            ip_address="127.0.0.1",
            user_agent="test_agent",
            permissions={"file_read", "web_access"},
            security_level=SecurityLevel.MEDIUM
        )
    
    def test_whitelist_commands(self, security_validator):
        """Test whitelisted commands"""
        whitelisted_commands = [
            "echo hello",
            "date",
            "whoami",
            "pwd",
            "ls -la"
        ]
        
        for cmd in whitelisted_commands:
            is_whitelisted = security_validator._is_whitelisted(cmd)
            assert is_whitelisted is True
    
    def test_blacklist_commands(self, security_validator):
        """Test blacklisted commands"""
        blacklisted_commands = [
            "rm -rf /",
            "format c:",
            "dd if=/dev/zero of=/dev/sda"
        ]
        
        for cmd in blacklisted_commands:
            is_blacklisted = security_validator._is_blacklisted(cmd)
            assert is_blacklisted is True
    
    @pytest.mark.asyncio
    async def test_command_validation(self, security_validator, sample_context):
        """Test command validation"""
        # Test safe command
        safe_result = await security_validator.validate_command(
            "echo hello", sample_context
        )
        assert safe_result.is_safe is True
        assert safe_result.threat_level == SecurityLevel.LOW
        
        # Test dangerous command
        dangerous_result = await security_validator.validate_command(
            "rm -rf /", sample_context
        )
        assert dangerous_result.is_safe is False
        assert dangerous_result.threat_level == SecurityLevel.CRITICAL
    
    def test_threat_detection(self, security_validator):
        """Test threat detection patterns"""
        # Test injection patterns
        injection_commands = [
            "echo hello; rm -rf /",
            "ls | cat /etc/passwd",
            "echo `whoami`"
        ]
        
        for cmd in injection_commands:
            threats = []
            for rule in security_validator.security_rules:
                if re.search(rule.pattern, cmd, re.IGNORECASE):
                    threats.append(rule.threat_type)
            
            assert ThreatType.INJECTION in threats

class TestCapabilityManager:
    """Test capability manager integration"""
    
    @pytest.fixture
    def capability_manager(self):
        """Create capability manager"""
        return CapabilityManager()
    
    @pytest.mark.asyncio
    async def test_capability_registration(self, capability_manager):
        """Test capability registration"""
        # Initialize the manager
        await capability_manager.initialize()
        
        # Test getting all capabilities
        capabilities = await capability_manager.get_all_capabilities()
        assert len(capabilities) > 0
        
        # Test getting capabilities by type
        system_capabilities = await capability_manager.get_capabilities_by_type(CapabilityType.SYSTEM)
        assert len(system_capabilities) > 0
    
    @pytest.mark.asyncio
    async def test_capability_execution(self, capability_manager):
        """Test capability execution"""
        # Initialize the manager
        await capability_manager.initialize()
        
        # Test system volume capability
        result = await capability_manager.execute_capability(
            "system_volume",
            {"action": "set", "level": 50},
            {}
        )
        
        assert result['success'] is True
        assert 'message' in result

class TestIntegration:
    """Test end-to-end integration"""
    
    @pytest.mark.asyncio
    async def test_complete_command_flow(self):
        """Test complete intelligent command flow"""
        # This would test the full flow from command input to execution
        # including AI processing, capability selection, execution, and error handling
        
        # Mock the intelligent command processor
        with patch('src.features.command_processing.intelligent_command_processor.IntelligentCommandProcessor') as mock_processor:
            mock_instance = AsyncMock()
            mock_instance.process_intelligent_command.return_value = {
                'success': True,
                'message': 'Command executed successfully',
                'steps': []
            }
            mock_processor.return_value = mock_instance
            
            # Test would go here
            pass

# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Test markers
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration
]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
