import asyncio
import sys
sys.path.insert(0, 'src')

from features.command_processing.capability_system import get_capability_manager

async def test_capabilities():
    manager = await get_capability_manager()
    await manager.initialize()
    capabilities = await manager.get_all_capabilities()
    
    print("Available capabilities:")
    for cap in capabilities:
        print(f"- {cap.name}")
    
    # Test system_info capability
    result = await manager.execute_capability(
        "system_info",
        {"info_type": "all"},
        {}
    )
    print(f"\nSystem info test: {result}")

if __name__ == "__main__":
    asyncio.run(test_capabilities())
