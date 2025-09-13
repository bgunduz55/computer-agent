# 🔌 JARVIS Computer Assistant - API Dokümantasyonu

Bu dokümantasyon, JARVIS Computer Assistant'ın API'lerini ve entegrasyon yöntemlerini detaylı olarak açıklar.

## 📋 **İçindekiler**

- [WebSocket API](#websocket-api)
- [REST API](#rest-api)
- [Plugin API](#plugin-api)
- [Analytics API](#analytics-api)
- [Security API](#security-api)
- [Python SDK](#python-sdk)
- [JavaScript SDK](#javascript-sdk)

## 🌐 **WebSocket API**

### **Bağlantı**

```javascript
const ws = new WebSocket('ws://localhost:8765');
```

### **Mesaj Formatı**

Tüm WebSocket mesajları JSON formatında gönderilir:

```json
{
  "type": "message_type",
  "data": {
    // Message specific data
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "id": "unique_message_id"
}
```

### **Mesaj Tipleri**

#### **1. Voice Command**

Ses komutu gönderme:

```json
{
  "type": "voice_command",
  "data": {
    "command": "What time is it?",
    "user_id": "user123",
    "session_id": "session456"
  },
  "id": "cmd_001"
}
```

**Yanıt:**
```json
{
  "type": "voice_command_response",
  "data": {
    "command": "What time is it?",
    "response": "It's currently 3:30 PM",
    "success": true,
    "processing_time_ms": 1250
  },
  "id": "cmd_001"
}
```

#### **2. System Status**

Sistem durumu sorgulama:

```json
{
  "type": "get_status",
  "data": {},
  "id": "status_001"
}
```

**Yanıt:**
```json
{
  "type": "status_response",
  "data": {
    "status": "running",
    "services": {
      "speech_manager": true,
      "ai_manager": true,
      "plugin_manager": true,
      "performance_manager": true,
      "security_manager": true,
      "analytics_manager": true
    },
    "uptime": 3600,
    "memory_usage": 45.2,
    "cpu_usage": 12.5
  },
  "id": "status_001"
}
```

#### **3. Plugin Control**

Plugin yönetimi:

```json
{
  "type": "plugin_control",
  "data": {
    "action": "start|stop|restart|status",
    "plugin_name": "weather",
    "config": {
      "api_key": "your-api-key"
    }
  },
  "id": "plugin_001"
}
```

#### **4. Analytics Query**

Analytics verilerini sorgulama:

```json
{
  "type": "analytics_query",
  "data": {
    "query_type": "usage|performance|security",
    "period_hours": 24,
    "filters": {
      "user_id": "user123",
      "component": "voice_recognition"
    }
  },
  "id": "analytics_001"
}
```

### **Event Streams**

#### **Real-time Events**

```json
{
  "type": "event",
  "data": {
    "event_type": "voice_command_received",
    "event_data": {
      "command": "Open Google",
      "user_id": "user123",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  }
}
```

#### **System Events**

```json
{
  "type": "system_event",
  "data": {
    "event_type": "plugin_loaded",
    "severity": "info",
    "message": "Weather plugin loaded successfully",
    "component": "plugin_manager",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## 🔗 **REST API**

### **Base URL**
```
http://localhost:8765/api
```

### **Authentication**

Tüm API istekleri için JWT token gerekli:

```http
Authorization: Bearer <your-jwt-token>
```

### **Endpoints**

#### **1. Authentication**

**POST /auth/login**
```json
{
  "user_id": "user123",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_at": "2024-01-02T00:00:00Z",
  "permissions": ["basic_access", "voice_commands", "system_info"]
}
```

**POST /auth/logout**
```json
{
  "token": "your-jwt-token"
}
```

#### **2. Voice Commands**

**POST /voice/command**
```json
{
  "command": "What time is it?",
  "user_id": "user123",
  "session_id": "session456"
}
```

**Response:**
```json
{
  "success": true,
  "response": "It's currently 3:30 PM",
  "processing_time_ms": 1250,
  "plugin_used": "system_info"
}
```

#### **3. System Management**

**GET /system/status**
```json
{
  "status": "running",
  "uptime": 3600,
  "services": {
    "speech_manager": true,
    "ai_manager": true,
    "plugin_manager": true
  },
  "performance": {
    "cpu_usage": 12.5,
    "memory_usage": 45.2,
    "response_time_avg": 850
  }
}
```

**POST /system/restart**
```json
{
  "component": "plugin_manager|all"
}
```

#### **4. Plugin Management**

**GET /plugins**
```json
{
  "plugins": [
    {
      "name": "weather",
      "version": "1.0.0",
      "status": "running",
      "enabled": true,
      "uptime": 3600
    }
  ]
}
```

**POST /plugins/{plugin_name}/start**
**POST /plugins/{plugin_name}/stop**
**POST /plugins/{plugin_name}/restart**

#### **5. Analytics**

**GET /analytics/usage**
```json
{
  "period_hours": 24,
  "total_commands": 150,
  "success_rate": 95.5,
  "avg_response_time": 850,
  "top_commands": [
    {"command": "what time is it", "count": 25},
    {"command": "open google", "count": 20}
  ]
}
```

**GET /analytics/performance**
```json
{
  "period_hours": 24,
  "cpu_usage": {
    "avg": 15.2,
    "max": 45.8,
    "min": 5.1
  },
  "memory_usage": {
    "avg": 42.5,
    "max": 65.2,
    "min": 35.1
  },
  "response_times": {
    "avg": 850,
    "max": 2500,
    "min": 200
  }
}
```

## 🔌 **Plugin API**

### **Base Plugin Class**

```python
from plugins.base_plugin import BasePlugin, PluginInfo, PluginType

class MyPlugin(BasePlugin):
    PLUGIN_INFO = PluginInfo(
        name="my_plugin",
        version="1.0.0",
        description="My custom plugin",
        author="Your Name",
        plugin_type=PluginType.UTILITY,
        dependencies=[],
        config_schema={
            "type": "object",
            "properties": {
                "api_key": {"type": "string"},
                "enabled": {"type": "boolean", "default": True}
            }
        }
    )
    
    async def _initialize(self) -> bool:
        # Plugin initialization
        return True
    
    async def _cleanup(self) -> None:
        # Plugin cleanup
        pass
    
    async def _start(self) -> bool:
        # Start plugin
        return True
    
    async def _stop(self) -> None:
        # Stop plugin
        pass
    
    async def handle_voice_command(self, command: str, context: Dict[str, Any] = None) -> Optional[str]:
        # Handle voice commands
        if "my command" in command.lower():
            return "Plugin response"
        return None
    
    async def handle_ai_request(self, request: str, context: Dict[str, Any] = None) -> Optional[str]:
        # Handle AI requests
        return None
    
    def get_commands(self) -> List[str]:
        return ["my command", "plugin test"]
    
    def get_capabilities(self) -> List[str]:
        return ["voice_commands", "ai_requests"]
```

### **Plugin Events**

```python
# Plugin event handling
def on_plugin_event(event_type: str, data: Any):
    if event_type == "voice_command_received":
        # Handle voice command
        pass
    elif event_type == "system_startup":
        # Handle system startup
        pass

# Register event handler
plugin.add_event_handler("voice_command_received", on_plugin_event)
```

### **Plugin Configuration**

```python
# Plugin configuration schema
config_schema = {
    "type": "object",
    "properties": {
        "api_key": {
            "type": "string",
            "description": "API key for external service"
        },
        "enabled": {
            "type": "boolean",
            "default": True,
            "description": "Enable/disable plugin"
        },
        "settings": {
            "type": "object",
            "properties": {
                "timeout": {"type": "integer", "default": 30},
                "retries": {"type": "integer", "default": 3}
            }
        }
    },
    "required": ["api_key"]
}
```

## 📊 **Analytics API**

### **Metrics Collection**

```python
from core.analytics_manager import get_analytics_manager

analytics = get_analytics_manager()

# Record custom metric
analytics.record_metric(
    metric_type="custom_metric",
    value=42.5,
    unit="count",
    tags={"component": "my_plugin", "user_id": "user123"}
)

# Track user action
analytics.track_user_action(
    action_type="button_click",
    action_data={"button": "submit", "form": "contact"},
    user_id="user123",
    session_id="session456",
    duration_ms=150,
    success=True
)

# Track system event
analytics.track_system_event(
    event_type="plugin_error",
    severity="error",
    message="Plugin failed to initialize",
    component="my_plugin",
    metadata={"error_code": "INIT_FAILED"}
)
```

### **Report Generation**

```python
# Generate usage report
usage_report = analytics.generate_report("usage", period_hours=24)
print(f"Total commands: {usage_report.data['total_actions']}")
print(f"Success rate: {usage_report.data['success_rate']}%")

# Generate performance report
perf_report = analytics.generate_report("performance", period_hours=24)
print(f"Avg CPU usage: {perf_report.data['cpu_usage']['avg']}%")
print(f"Avg response time: {perf_report.data['response_times']['avg']}ms")
```

## 🔒 **Security API**

### **Command Validation**

```python
from core.security_manager import get_security_manager

security = get_security_manager()

# Validate command
is_valid = await security.validate_command(
    command="ls -la",
    user_id="user123"
)

if not is_valid:
    print("Command blocked for security reasons")
```

### **Authentication**

```python
# Authenticate user
token = await security.authenticate_user(
    user_id="user123",
    password="password123"
)

if token:
    print(f"Token: {token.token}")
    print(f"Expires: {token.expires_at}")
else:
    print("Authentication failed")

# Validate token
valid_token = await security.validate_token(token.token)
if valid_token:
    print(f"User: {valid_token.user_id}")
    print(f"Permissions: {valid_token.permissions}")
```

### **Data Encryption**

```python
# Encrypt sensitive data
encrypted_data = security.encrypt_sensitive_data("sensitive information")
print(f"Encrypted: {encrypted_data}")

# Decrypt data
decrypted_data = security.decrypt_sensitive_data(encrypted_data)
print(f"Decrypted: {decrypted_data}")
```

## 🐍 **Python SDK**

### **Installation**

```bash
pip install jarvis-assistant-sdk
```

### **Basic Usage**

```python
from jarvis_sdk import JARVISClient

# Initialize client
client = JARVISClient(
    host="localhost",
    port=8765,
    use_ssl=False
)

# Connect
await client.connect()

# Send voice command
response = await client.send_voice_command("What time is it?")
print(f"Response: {response.content}")

# Get system status
status = await client.get_system_status()
print(f"Status: {status.status}")

# Disconnect
await client.disconnect()
```

### **Advanced Usage**

```python
# With authentication
client = JARVISClient(
    host="localhost",
    port=8765,
    auth_token="your-jwt-token"
)

# Event handling
async def on_voice_command(event):
    print(f"Voice command: {event.data['command']}")

client.add_event_handler("voice_command_received", on_voice_command)

# Plugin management
plugins = await client.get_plugins()
await client.start_plugin("weather")
await client.stop_plugin("weather")

# Analytics
usage_report = await client.get_analytics_report("usage", period_hours=24)
```

## 🌐 **JavaScript SDK**

### **Installation**

```bash
npm install jarvis-assistant-sdk
```

### **Basic Usage**

```javascript
import { JARVISClient } from 'jarvis-assistant-sdk';

// Initialize client
const client = new JARVISClient({
  host: 'localhost',
  port: 8765,
  useSSL: false
});

// Connect
await client.connect();

// Send voice command
const response = await client.sendVoiceCommand('What time is it?');
console.log('Response:', response.content);

// Get system status
const status = await client.getSystemStatus();
console.log('Status:', status.status);

// Disconnect
await client.disconnect();
```

### **Advanced Usage**

```javascript
// With authentication
const client = new JARVISClient({
  host: 'localhost',
  port: 8765,
  authToken: 'your-jwt-token'
});

// Event handling
client.on('voice_command_received', (event) => {
  console.log('Voice command:', event.data.command);
});

// Plugin management
const plugins = await client.getPlugins();
await client.startPlugin('weather');
await client.stopPlugin('weather');

// Analytics
const usageReport = await client.getAnalyticsReport('usage', 24);
```

## 📝 **Error Handling**

### **Common Error Codes**

| Code | Description | Solution |
|------|-------------|----------|
| `AUTH_REQUIRED` | Authentication required | Provide valid JWT token |
| `INVALID_TOKEN` | Invalid or expired token | Refresh token or re-authenticate |
| `COMMAND_BLOCKED` | Command blocked by security | Check command against security policy |
| `PLUGIN_NOT_FOUND` | Plugin not found | Verify plugin name and availability |
| `RATE_LIMITED` | Too many requests | Wait and retry with backoff |
| `INTERNAL_ERROR` | Internal server error | Check logs and contact support |

### **Error Response Format**

```json
{
  "success": false,
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Authentication required",
    "details": {
      "required_permissions": ["basic_access"]
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔧 **Rate Limiting**

### **Limits**

- **Voice Commands**: 60 requests/minute
- **API Calls**: 1000 requests/hour
- **WebSocket Messages**: 100 messages/minute

### **Headers**

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## 📚 **Examples**

### **Complete Voice Command Example**

```python
import asyncio
from jarvis_sdk import JARVISClient

async def main():
    client = JARVISClient(host="localhost", port=8765)
    
    try:
        await client.connect()
        
        # Send voice command
        response = await client.send_voice_command("What's the weather like?")
        print(f"JARVIS: {response.content}")
        
        # Check if command was successful
        if response.success:
            print("Command executed successfully")
        else:
            print(f"Command failed: {response.error}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()

asyncio.run(main())
```

### **Real-time Event Monitoring**

```python
import asyncio
from jarvis_sdk import JARVISClient

async def main():
    client = JARVISClient(host="localhost", port=8765)
    
    # Event handlers
    async def on_voice_command(event):
        print(f"Voice command received: {event.data['command']}")
    
    async def on_system_event(event):
        print(f"System event: {event.data['message']}")
    
    # Register handlers
    client.add_event_handler("voice_command_received", on_voice_command)
    client.add_event_handler("system_event", on_system_event)
    
    try:
        await client.connect()
        print("Connected. Listening for events...")
        
        # Keep connection alive
        await asyncio.sleep(60)
        
    except KeyboardInterrupt:
        print("Disconnecting...")
    finally:
        await client.disconnect()

asyncio.run(main())
```

---

**Daha fazla bilgi için:**
- [GitHub Repository](https://github.com/yourusername/jarvis-computer-assistant)
- [Discord Community](https://discord.gg/jarvis-assistant)
- [Documentation Website](https://docs.jarvis-assistant.com)
