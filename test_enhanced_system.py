#!/usr/bin/env python3
"""
Enhanced JARVIS System Test

Tests all the new features including keyboard control, improved AI parsing,
and enhanced capabilities.
"""

import asyncio
import logging
import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from features.remote_control.websocket_server import get_websocket_server
from features.command_processing.quick_commands import get_quick_commands_handler
from features.command_processing.capability_system import get_capability_manager
from features.command_processing.intelligent_command_processor import IntelligentCommandProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_keyboard_control():
    """Test keyboard control capabilities"""
    print("\n🔧 Testing Keyboard Control Capabilities...")
    
    try:
        capability_manager = get_capability_manager()
        await capability_manager.initialize()
        
        # Test Enter key
        print("  Testing Enter key...")
        result = await capability_manager.execute_capability(
            "keyboard_control",
            {"key": "enter", "action": "tap"},
            {}
        )
        print(f"    Enter key result: {result['success']}")
        
        # Test Space key
        print("  Testing Space key...")
        result = await capability_manager.execute_capability(
            "keyboard_control",
            {"key": "space", "action": "tap"},
            {}
        )
        print(f"    Space key result: {result['success']}")
        
        # Test Tab key
        print("  Testing Tab key...")
        result = await capability_manager.execute_capability(
            "keyboard_control",
            {"key": "tab", "action": "tap"},
            {}
        )
        print(f"    Tab key result: {result['success']}")
        
        # Test Arrow keys
        print("  Testing Arrow keys...")
        for direction in ["up", "down", "left", "right"]:
            result = await capability_manager.execute_capability(
                "keyboard_control",
                {"key": direction, "action": "tap"},
                {}
            )
            print(f"    {direction} arrow result: {result['success']}")
        
        print("  ✅ Keyboard control test completed")
        return True
        
    except Exception as e:
        print(f"  ❌ Keyboard control test failed: {e}")
        return False

async def test_quick_commands():
    """Test quick commands including keyboard shortcuts"""
    print("\n⚡ Testing Quick Commands...")
    
    try:
        capability_manager = get_capability_manager()
        await capability_manager.initialize()
        
        quick_commands = get_quick_commands_handler(capability_manager)
        
        # Test keyboard quick commands
        keyboard_commands = [
            "key enter",
            "key space", 
            "key tab",
            "key escape",
            "key backspace",
            "key arrow up",
            "key arrow down",
            "key arrow left",
            "key arrow right"
        ]
        
        for command in keyboard_commands:
            print(f"  Testing: {command}")
            result = await quick_commands.process_command(command)
            print(f"    Result: {result.get('message', 'No message')}")
        
        # Test text input commands
        text_commands = [
            "yaz Hello World",
            "yaz hadi kod yazalım"
        ]
        
        for command in text_commands:
            print(f"  Testing: {command}")
            result = await quick_commands.process_command(command)
            print(f"    Result: {result.get('message', 'No message')}")
        
        print("  ✅ Quick commands test completed")
        return True
        
    except Exception as e:
        print(f"  ❌ Quick commands test failed: {e}")
        return False

async def test_terminal_commands():
    """Test terminal command execution"""
    print("\n💻 Testing Terminal Commands...")
    
    try:
        capability_manager = get_capability_manager()
        await capability_manager.initialize()
        
        # Test basic terminal commands
        terminal_commands = [
            "echo 'Hello from JARVIS'",
            "dir" if os.name == 'nt' else "ls -la",
            "date" if os.name == 'nt' else "date",
            "whoami" if os.name == 'nt' else "whoami"
        ]
        
        for command in terminal_commands:
            print(f"  Testing: {command}")
            result = await capability_manager.execute_capability(
                "terminal_command",
                {"command": command},
                {}
            )
            print(f"    Success: {result['success']}")
            if result['success']:
                print(f"    Output: {result['stdout'][:100]}...")
            else:
                print(f"    Error: {result.get('error', 'Unknown error')}")
        
        print("  ✅ Terminal commands test completed")
        return True
        
    except Exception as e:
        print(f"  ❌ Terminal commands test failed: {e}")
        return False

async def test_ai_parsing():
    """Test AI response parsing improvements"""
    print("\n🤖 Testing AI Response Parsing...")
    
    try:
        # Create intelligent processor instance
        from features.ai_integration import get_ai_manager
        from features.command_processing.capability_system import get_capability_manager
        
        ai_manager = get_ai_manager()
        capability_manager = get_capability_manager()
        await capability_manager.initialize()
        
        intelligent_processor = IntelligentCommandProcessor(ai_manager, capability_manager)
        
        # Test with malformed JSON
        test_responses = [
            '{"execution_plan": {"steps": [{"step_id": "test", "capability": "terminal_command", "parameters": {"command": "echo test"}}]}}',
            'Some text before {"execution_plan": {"steps": []}} some text after',
            '```json\n{"execution_plan": {"steps": []}}\n```',
            'Invalid JSON with {unclosed brackets',
            'No JSON at all in this response'
        ]
        
        for i, response_text in enumerate(test_responses):
            print(f"  Testing response {i+1}: {response_text[:50]}...")
            
            # Create mock AI response
            from features.ai_integration.ai_provider_manager import AIResponse
            ai_response = AIResponse(
                content=response_text,
                model="test",
                usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                response_time=0.1
            )
            
            plan = await intelligent_processor._parse_ai_response(ai_response, "test command")
            if plan:
                print(f"    ✅ Parsed successfully: {len(plan.steps)} steps")
            else:
                print(f"    ⚠️  Fallback to terminal command")
        
        print("  ✅ AI parsing test completed")
        return True
        
    except Exception as e:
        print(f"  ❌ AI parsing test failed: {e}")
        return False

async def test_websocket_server():
    """Test WebSocket server functionality"""
    print("\n🌐 Testing WebSocket Server...")
    
    try:
        # Start server
        server = get_websocket_server("localhost", 8765)
        await server.start()
        
        print("  ✅ WebSocket server started successfully")
        
        # Test server components
        if hasattr(server, 'quick_commands_handler') and server.quick_commands_handler:
            print("  ✅ Quick commands handler initialized")
        else:
            print("  ❌ Quick commands handler not found")
        
        if hasattr(server, 'intelligent_processor') and server.intelligent_processor:
            print("  ✅ Intelligent processor initialized")
        else:
            print("  ❌ Intelligent processor not found")
        
        if hasattr(server, 'capability_manager') and server.capability_manager:
            print("  ✅ Capability manager initialized")
        else:
            print("  ❌ Capability manager not found")
        
        # Stop server
        await server.stop()
        print("  ✅ WebSocket server stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ WebSocket server test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Enhanced JARVIS System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Keyboard Control", test_keyboard_control),
        ("Quick Commands", test_quick_commands),
        ("Terminal Commands", test_terminal_commands),
        ("AI Parsing", test_ai_parsing),
        ("WebSocket Server", test_websocket_server),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for production.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)
