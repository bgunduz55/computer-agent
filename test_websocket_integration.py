import asyncio
import websockets
import json
import sys
sys.path.insert(0, 'src')

from features.remote_control.websocket_server import WebSocketServer

async def test_websocket_integration():
    """Test WebSocket server with intelligent command processing"""
    
    # Create WebSocket server
    server = WebSocketServer(host="localhost", port=8766)
    
    # Initialize server
    if not await server.initialize():
        print("❌ Failed to initialize WebSocket server")
        return
    
    print("✅ WebSocket server initialized")
    
    # Start server
    await server.start()
    print("✅ WebSocket server started on localhost:8766")
    
    # Test client connection
    try:
        async with websockets.connect("ws://localhost:8766") as websocket:
            print("✅ Connected to WebSocket server")
            
            # Test voice command
            voice_command = {
                "type": "voice_command",
                "data": {
                    "command": "show system info"
                }
            }
            
            await websocket.send(json.dumps(voice_command))
            print("✅ Sent voice command: 'show system info'")
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
            response_data = json.loads(response)
            
            print(f"✅ Received response: {response_data}")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
    
    finally:
        # Stop server
        await server.stop()
        print("✅ WebSocket server stopped")

if __name__ == "__main__":
    asyncio.run(test_websocket_integration())
