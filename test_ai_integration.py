import asyncio
import sys
sys.path.insert(0, 'src')

from features.command_processing.intelligent_command_processor import IntelligentCommandProcessor
from features.ai_integration.ai_provider_manager import AIProviderManager
from features.command_processing.capability_system import get_capability_manager

async def test_ai_integration():
    """Test AI integration with intelligent command processor"""
    
    # Initialize AI manager
    ai_manager = AIProviderManager()
    ai_manager.initialize()
    
    # Initialize capability manager
    capability_manager = await get_capability_manager()
    await capability_manager.initialize()
    
    # Create intelligent command processor
    processor = IntelligentCommandProcessor(ai_manager, capability_manager)
    await processor.initialize()
    
    # Test simple command
    print("Testing simple command: 'show system info'")
    result = await processor.process_intelligent_command("show system info", {})
    print(f"Result: {result.success}")
    print(f"Message: {result.message}")
    print(f"Steps executed: {result.steps_executed}")
    print(f"Execution time: {result.execution_time:.2f}s")
    
    if result.error:
        print(f"Error: {result.error}")

if __name__ == "__main__":
    asyncio.run(test_ai_integration())
