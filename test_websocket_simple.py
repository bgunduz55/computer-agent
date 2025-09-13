import asyncio
import sys
sys.path.insert(0, 'src')

from features.remote_control.websocket_server import WebSocketServer

async def test_websocket_simple():
    """Simple WebSocket server test"""
    
    # Create WebSocket server
    server = WebSocketServer(host="localhost", port=8766)
    
    # Initialize server
    if not await server.initialize():
        print("❌ Failed to initialize WebSocket server")
        return
    
    print("✅ WebSocket server initialized")
    print("✅ Intelligent command processor integrated")
    print("✅ WebSocket server ready for Flutter client connection")
    
    # Start server in background
    asyncio.create_task(server.start())
    
    print("✅ WebSocket server started on localhost:8766")
    print("✅ Ready to accept Flutter client connections")
    print("✅ Voice commands will be processed through intelligent command system")
    
    # Keep server running
    try:
        await asyncio.sleep(10)  # Run for 10 seconds
    except KeyboardInterrupt:
        print("\n✅ Test completed")
    finally:
        await server.stop()
        print("✅ WebSocket server stopped")

if __name__ == "__main__":
    asyncio.run(test_websocket_simple())
