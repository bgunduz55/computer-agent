"""
WhatsApp Automation Capabilities

Advanced WhatsApp Web automation including messaging, group management,
and file sharing with intelligent contact detection.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from integrations.browser_automation import WebAutomationExecutor, BrowserConfig, BrowserType, BrowserBackend
from integrations.browser_automation.element_finder import FindStrategy, ElementType
from ..capability_system import BaseCapabilityExecutor

logger = logging.getLogger(__name__)

@dataclass
class WhatsAppContact:
    """WhatsApp contact information"""
    name: str
    phone: str
    last_seen: str = ""
    status: str = ""
    profile_picture: str = ""

@dataclass
class WhatsAppMessage:
    """WhatsApp message information"""
    sender: str
    content: str
    timestamp: str
    message_type: str = "text"

class WhatsAppAutomationExecutor(BaseCapabilityExecutor):
    """Advanced WhatsApp Web automation executor"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.automation_executor: Optional[WebAutomationExecutor] = None
        self._is_initialized = False
        self._is_logged_in = False
    
    async def initialize(self) -> bool:
        """Initialize WhatsApp automation executor"""
        try:
            # Create browser configuration for WhatsApp Web
            config = BrowserConfig(
                browser_type=BrowserType.CHROME,
                backend=BrowserBackend.SELENIUM,
                headless=False,  # WhatsApp Web needs visual interaction
                window_size=(1920, 1080),
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            self.automation_executor = WebAutomationExecutor(config)
            success = await self.automation_executor.initialize()
            
            if success:
                self._is_initialized = True
                self.logger.info("WhatsApp automation executor initialized successfully")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WhatsApp automation executor: {e}")
            return False
    
    def is_initialized(self) -> bool:
        """Check if executor is initialized"""
        return self._is_initialized
    
    def can_execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Check if WhatsApp automation can be executed"""
        action = parameters.get('action', 'send_message')
        return action in ['send_message', 'send_file', 'create_group', 'add_to_group', 'get_contacts', 'get_messages']
    
    async def execute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute WhatsApp automation operation"""
        try:
            if not self._is_initialized:
                return {"success": False, "error": "WhatsApp automation executor not initialized"}
            
            # Check if logged in, if not, try to login
            if not self._is_logged_in:
                login_result = await self._ensure_logged_in()
                if not login_result:
                    return {"success": False, "error": "Failed to login to WhatsApp Web"}
            
            action = parameters.get('action', 'send_message')
            contact = parameters.get('contact', '')
            message = parameters.get('message', '')
            file_path = parameters.get('file_path', '')
            group_name = parameters.get('group_name', '')
            
            if action == "send_message":
                return await self._send_message(contact, message)
            elif action == "send_file":
                return await self._send_file(contact, file_path, message)
            elif action == "create_group":
                return await self._create_group(group_name, parameters.get('members', []))
            elif action == "add_to_group":
                return await self._add_to_group(parameters.get('group_name', ''), parameters.get('members', []))
            elif action == "get_contacts":
                return await self._get_contacts()
            elif action == "get_messages":
                return await self._get_messages(contact)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Error executing WhatsApp automation: {e}")
            return {"success": False, "error": str(e)}
    
    async def _ensure_logged_in(self) -> bool:
        """Ensure user is logged in to WhatsApp Web"""
        try:
            # Navigate to WhatsApp Web
            nav_result = await self.automation_executor.navigate_to("https://web.whatsapp.com")
            if not nav_result.success:
                return False
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Check if already logged in by looking for chat list
            chat_list_result = await self.automation_executor.wait_for_element(
                locator="div[data-testid='chat-list']",
                strategy=FindStrategy.CSS_SELECTOR,
                timeout=5
            )
            
            if chat_list_result.success:
                self._is_logged_in = True
                return True
            
            # Check if QR code is displayed (need to scan)
            qr_result = await self.automation_executor.wait_for_element(
                locator="div[data-testid='qr-code']",
                strategy=FindStrategy.CSS_SELECTOR,
                timeout=5
            )
            
            if qr_result.success:
                self.logger.info("QR code detected. Please scan with your phone to login.")
                # Wait for user to scan QR code
                for i in range(60):  # Wait up to 5 minutes
                    await asyncio.sleep(5)
                    
                    # Check if logged in
                    chat_list_result = await self.automation_executor.wait_for_element(
                        locator="div[data-testid='chat-list']",
                        strategy=FindStrategy.CSS_SELECTOR,
                        timeout=2
                    )
                    
                    if chat_list_result.success:
                        self._is_logged_in = True
                        self.logger.info("Successfully logged in to WhatsApp Web")
                        return True
                
                return False
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to ensure login: {e}")
            return False
    
    async def _send_message(self, contact: str, message: str) -> Dict[str, Any]:
        """Send a message to a contact"""
        try:
            # Search for contact
            search_result = await self._search_contact(contact)
            if not search_result["success"]:
                return search_result
            
            # Click on contact
            click_result = await self.automation_executor.click_element(
                locator=f"span[title='{contact}']",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.LINK
            )
            
            if not click_result.success:
                return {"success": False, "error": f"Failed to select contact: {contact}"}
            
            # Wait for chat to open
            await asyncio.sleep(2)
            
            # Find message input box
            input_result = await self.automation_executor.wait_for_element(
                locator="div[data-testid='conversation-compose-box-input']",
                strategy=FindStrategy.CSS_SELECTOR,
                timeout=10
            )
            
            if not input_result.success:
                return {"success": False, "error": "Failed to find message input box"}
            
            # Type message
            type_result = await self.automation_executor.type_text(
                locator="div[data-testid='conversation-compose-box-input']",
                text=message,
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.INPUT
            )
            
            if not type_result.success:
                return {"success": False, "error": "Failed to type message"}
            
            # Send message (press Enter)
            send_result = await self.automation_executor.execute_javascript(
                "document.querySelector('div[data-testid=\"conversation-compose-box-input\"]').dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter'}))"
            )
            
            return {
                "success": True,
                "message": f"Message sent to {contact}",
                "data": {
                    "contact": contact,
                    "message": message,
                    "timestamp": time.time()
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to send message: {e}"}
    
    async def _send_file(self, contact: str, file_path: str, message: str = "") -> Dict[str, Any]:
        """Send a file to a contact"""
        try:
            # Search for contact
            search_result = await self._search_contact(contact)
            if not search_result["success"]:
                return search_result
            
            # Click on contact
            click_result = await self.automation_executor.click_element(
                locator=f"span[title='{contact}']",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.LINK
            )
            
            if not click_result.success:
                return {"success": False, "error": f"Failed to select contact: {contact}"}
            
            # Wait for chat to open
            await asyncio.sleep(2)
            
            # Click attachment button
            attach_result = await self.automation_executor.click_element(
                locator="div[data-testid='attach-document']",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.BUTTON
            )
            
            if not attach_result.success:
                return {"success": False, "error": "Failed to find attachment button"}
            
            # Wait for file input to appear
            await asyncio.sleep(1)
            
            # Upload file using JavaScript
            upload_script = f"""
                const input = document.querySelector('input[type="file"]');
                if (input) {{
                    const file = new File([''], '{file_path}');
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    input.files = dataTransfer.files;
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            """
            
            upload_result = await self.automation_executor.execute_javascript(upload_script)
            
            # Add message if provided
            if message:
                message_result = await self.automation_executor.type_text(
                    locator="div[data-testid='conversation-compose-box-input']",
                    text=message,
                    strategy=FindStrategy.CSS_SELECTOR,
                    element_type=ElementType.INPUT
                )
            
            # Send file
            send_result = await self.automation_executor.click_element(
                locator="span[data-testid='send']",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.BUTTON
            )
            
            return {
                "success": True,
                "message": f"File sent to {contact}",
                "data": {
                    "contact": contact,
                    "file_path": file_path,
                    "message": message,
                    "timestamp": time.time()
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to send file: {e}"}
    
    async def _search_contact(self, contact: str) -> Dict[str, Any]:
        """Search for a contact in WhatsApp"""
        try:
            # Click on search box
            search_click_result = await self.automation_executor.click_element(
                locator="div[data-testid='chat-list-search']",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.INPUT
            )
            
            if not search_click_result.success:
                return {"success": False, "error": "Failed to find search box"}
            
            # Type contact name
            type_result = await self.automation_executor.type_text(
                locator="div[data-testid='chat-list-search']",
                text=contact,
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.INPUT
            )
            
            if not type_result.success:
                return {"success": False, "error": "Failed to type contact name"}
            
            # Wait for search results
            await asyncio.sleep(2)
            
            # Check if contact is found
            contact_result = await self.automation_executor.wait_for_element(
                locator=f"span[title='{contact}']",
                strategy=FindStrategy.CSS_SELECTOR,
                timeout=5
            )
            
            if contact_result.success:
                return {"success": True, "message": f"Contact found: {contact}"}
            else:
                return {"success": False, "error": f"Contact not found: {contact}"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to search contact: {e}"}
    
    async def _create_group(self, group_name: str, members: List[str]) -> Dict[str, Any]:
        """Create a new WhatsApp group"""
        try:
            # Click on new chat button
            new_chat_result = await self.automation_executor.click_element(
                locator="div[data-testid='new-chat']",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.BUTTON
            )
            
            if not new_chat_result.success:
                return {"success": False, "error": "Failed to find new chat button"}
            
            # Click on new group
            new_group_result = await self.automation_executor.click_element(
                locator="div[data-testid='new-group']",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.BUTTON
            )
            
            if not new_group_result.success:
                return {"success": False, "error": "Failed to find new group button"}
            
            # Add members
            for member in members:
                # Search for member
                search_result = await self._search_contact(member)
                if search_result["success"]:
                    # Click on member to add
                    add_result = await self.automation_executor.click_element(
                        locator=f"span[title='{member}']",
                        strategy=FindStrategy.CSS_SELECTOR,
                        element_type=ElementType.LINK
                    )
                    await asyncio.sleep(1)
            
            # Click next
            next_result = await self.automation_executor.click_element(
                locator="div[data-testid='group-name-input']",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.INPUT
            )
            
            # Type group name
            name_result = await self.automation_executor.type_text(
                locator="div[data-testid='group-name-input']",
                text=group_name,
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.INPUT
            )
            
            # Click create
            create_result = await self.automation_executor.click_element(
                locator="div[data-testid='group-create']",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.BUTTON
            )
            
            return {
                "success": True,
                "message": f"Group '{group_name}' created successfully",
                "data": {
                    "group_name": group_name,
                    "members": members,
                    "timestamp": time.time()
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to create group: {e}"}
    
    async def _add_to_group(self, group_name: str, members: List[str]) -> Dict[str, Any]:
        """Add members to an existing group"""
        try:
            # Search for group
            search_result = await self._search_contact(group_name)
            if not search_result["success"]:
                return search_result
            
            # Click on group
            click_result = await self.automation_executor.click_element(
                locator=f"span[title='{group_name}']",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.LINK
            )
            
            if not click_result.success:
                return {"success": False, "error": f"Failed to select group: {group_name}"}
            
            # Click on group info
            info_result = await self.automation_executor.click_element(
                locator="div[data-testid='group-info']",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.BUTTON
            )
            
            # Add members
            for member in members:
                # Click add member button
                add_result = await self.automation_executor.click_element(
                    locator="div[data-testid='add-member']",
                    strategy=FindStrategy.CSS_SELECTOR,
                    element_type=ElementType.BUTTON
                )
                
                # Search for member
                search_result = await self._search_contact(member)
                if search_result["success"]:
                    # Click on member to add
                    add_member_result = await self.automation_executor.click_element(
                        locator=f"span[title='{member}']",
                        strategy=FindStrategy.CSS_SELECTOR,
                        element_type=ElementType.LINK
                    )
                    await asyncio.sleep(1)
            
            return {
                "success": True,
                "message": f"Members added to group '{group_name}'",
                "data": {
                    "group_name": group_name,
                    "members": members,
                    "timestamp": time.time()
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to add members to group: {e}"}
    
    async def _get_contacts(self) -> Dict[str, Any]:
        """Get list of WhatsApp contacts"""
        try:
            # Navigate to contacts if not already there
            nav_result = await self.automation_executor.navigate_to("https://web.whatsapp.com")
            if not nav_result.success:
                return {"success": False, "error": "Failed to navigate to WhatsApp Web"}
            
            # Wait for contacts to load
            await asyncio.sleep(3)
            
            # Get contact elements
            contact_elements = await self.automation_executor.element_finder.find_elements(
                locator="div[data-testid='chat-list'] span[title]",
                strategy=FindStrategy.CSS_SELECTOR
            )
            
            contacts = []
            for element in contact_elements:
                try:
                    name_result = await self.automation_executor.get_text(
                        locator="span[title]",
                        strategy=FindStrategy.CSS_SELECTOR
                    )
                    
                    if name_result.success:
                        contact_name = name_result.data.get("text", "")
                        if contact_name:
                            contacts.append(WhatsAppContact(
                                name=contact_name,
                                phone="",  # Phone not easily accessible
                                last_seen="",
                                status=""
                            ))
                except:
                    continue
            
            return {
                "success": True,
                "message": f"Found {len(contacts)} contacts",
                "data": {
                    "contacts": [contact.__dict__ for contact in contacts],
                    "total_contacts": len(contacts)
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get contacts: {e}"}
    
    async def _get_messages(self, contact: str) -> Dict[str, Any]:
        """Get messages from a contact"""
        try:
            # Search for contact
            search_result = await self._search_contact(contact)
            if not search_result["success"]:
                return search_result
            
            # Click on contact
            click_result = await self.automation_executor.click_element(
                locator=f"span[title='{contact}']",
                strategy=FindStrategy.CSS_SELECTOR,
                element_type=ElementType.LINK
            )
            
            if not click_result.success:
                return {"success": False, "error": f"Failed to select contact: {contact}"}
            
            # Wait for messages to load
            await asyncio.sleep(2)
            
            # Get message elements
            message_elements = await self.automation_executor.element_finder.find_elements(
                locator="div[data-testid='conversation-panel-messages'] div[data-testid='msg-container']",
                strategy=FindStrategy.CSS_SELECTOR
            )
            
            messages = []
            for element in message_elements:
                try:
                    # Get message text
                    text_result = await self.automation_executor.get_text(
                        locator="span.selectable-text",
                        strategy=FindStrategy.CSS_SELECTOR
                    )
                    
                    if text_result.success:
                        message_text = text_result.data.get("text", "")
                        if message_text:
                            messages.append(WhatsAppMessage(
                                sender=contact,
                                content=message_text,
                                timestamp="",
                                message_type="text"
                            ))
                except:
                    continue
            
            return {
                "success": True,
                "message": f"Retrieved {len(messages)} messages from {contact}",
                "data": {
                    "contact": contact,
                    "messages": [message.__dict__ for message in messages],
                    "total_messages": len(messages)
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to get messages: {e}"}
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.automation_executor:
                await self.automation_executor.cleanup()
            self._is_initialized = False
            self._is_logged_in = False
            self.logger.info("WhatsApp automation executor cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

