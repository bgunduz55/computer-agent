"""
Email Plugin for JARVIS Computer Assistant
Provides email management and notifications
"""

import asyncio
import logging
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

from ..base_plugin import BasePlugin, PluginInfo, PluginType, PluginConfig


@dataclass
class EmailMessage:
    """Email message data"""
    subject: str
    sender: str
    recipient: str
    body: str
    timestamp: datetime
    is_read: bool = False
    message_id: str = ""


class EmailPlugin(BasePlugin):
    """Email management plugin"""
    
    PLUGIN_INFO = PluginInfo(
        name="email",
        version="1.0.0",
        description="Email management and notifications",
        author="JARVIS Team",
        plugin_type=PluginType.COMMUNICATION,
        dependencies=[],
        config_schema={
            "type": "object",
            "properties": {
                "smtp_server": {"type": "string", "description": "SMTP server address"},
                "smtp_port": {"type": "integer", "default": 587, "description": "SMTP server port"},
                "imap_server": {"type": "string", "description": "IMAP server address"},
                "imap_port": {"type": "integer", "default": 993, "description": "IMAP server port"},
                "email_address": {"type": "string", "description": "Email address"},
                "password": {"type": "string", "description": "Email password or app password"},
                "use_tls": {"type": "boolean", "default": True, "description": "Use TLS encryption"},
                "check_interval": {"type": "integer", "default": 300, "description": "Email check interval in seconds"}
            },
            "required": ["smtp_server", "imap_server", "email_address", "password"]
        }
    )
    
    PRIORITY = 70
    
    def __init__(self, plugin_info: PluginInfo, config: PluginConfig = None):
        super().__init__(plugin_info, config)
        self.smtp_server = None
        self.smtp_port = 587
        self.imap_server = None
        self.imap_port = 993
        self.email_address = None
        self.password = None
        self.use_tls = True
        self.check_interval = 300
        self._checking_task = None
        self._unread_count = 0
        self._last_check = None
        
    async def _initialize(self) -> bool:
        """Initialize email plugin"""
        try:
            # Load configuration
            settings = self.config.settings or {}
            self.smtp_server = settings.get("smtp_server")
            self.smtp_port = settings.get("smtp_port", 587)
            self.imap_server = settings.get("imap_server")
            self.imap_port = settings.get("imap_port", 993)
            self.email_address = settings.get("email_address")
            self.password = settings.get("password")
            self.use_tls = settings.get("use_tls", True)
            self.check_interval = settings.get("check_interval", 300)
            
            if not all([self.smtp_server, self.imap_server, self.email_address, self.password]):
                self.logger.warning("Email configuration incomplete")
                return False
            
            self.logger.info(f"Email plugin initialized for {self.email_address}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize email plugin: {e}")
            return False
    
    async def _cleanup(self) -> None:
        """Cleanup email plugin"""
        if self._checking_task:
            self._checking_task.cancel()
            try:
                await self._checking_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Email plugin cleaned up")
    
    async def _start(self) -> bool:
        """Start email monitoring"""
        try:
            # Start periodic email checking
            self._checking_task = asyncio.create_task(self._email_checking_loop())
            self.logger.info("Email monitoring started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start email monitoring: {e}")
            return False
    
    async def _stop(self) -> None:
        """Stop email monitoring"""
        if self._checking_task:
            self._checking_task.cancel()
            try:
                await self._checking_task
            except asyncio.CancelledError:
                pass
            self._checking_task = None
        
        self.logger.info("Email monitoring stopped")
    
    async def _email_checking_loop(self) -> None:
        """Periodic email checking loop"""
        while True:
            try:
                await self._check_new_emails()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in email checking loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _check_new_emails(self) -> None:
        """Check for new emails"""
        try:
            unread_count = await self.get_unread_count()
            
            if unread_count > self._unread_count:
                new_emails = unread_count - self._unread_count
                self.logger.info(f"You have {new_emails} new email(s)")
                
                # Emit new email event
                self.emit_event("new_emails", {
                    "count": new_emails,
                    "total_unread": unread_count
                })
            
            self._unread_count = unread_count
            self._last_check = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error checking emails: {e}")
    
    async def handle_voice_command(self, command: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Handle email-related voice commands"""
        command_lower = command.lower()
        
        if any(keyword in command_lower for keyword in ["email", "mail", "e-posta", "message", "mesaj"]):
            try:
                if "unread" in command_lower or "okunmamış" in command_lower:
                    count = await self.get_unread_count()
                    return f"You have {count} unread emails."
                elif "check" in command_lower or "kontrol" in command_lower:
                    await self._check_new_emails()
                    return f"You have {self._unread_count} unread emails."
                elif "send" in command_lower or "gönder" in command_lower:
                    return "I can help you send emails. Please provide the recipient and message."
                else:
                    count = await self.get_unread_count()
                    return f"You have {count} unread emails. Would you like me to check for new messages?"
                    
            except Exception as e:
                self.logger.error(f"Error handling email command: {e}")
                return "Sorry, I couldn't access your email right now."
        
        return None
    
    async def get_unread_count(self) -> int:
        """Get count of unread emails"""
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.password)
            mail.select('INBOX')
            
            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')
            
            if status == 'OK':
                unread_count = len(messages[0].split())
                mail.close()
                mail.logout()
                return unread_count
            else:
                mail.close()
                mail.logout()
                return 0
                
        except Exception as e:
            self.logger.error(f"Error getting unread count: {e}")
            return 0
    
    async def get_recent_emails(self, limit: int = 5) -> List[EmailMessage]:
        """Get recent emails"""
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.password)
            mail.select('INBOX')
            
            # Search for recent emails
            status, messages = mail.search(None, 'ALL')
            
            if status != 'OK':
                mail.close()
                mail.logout()
                return []
            
            email_ids = messages[0].split()
            recent_emails = []
            
            # Get the most recent emails
            for email_id in email_ids[-limit:]:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                
                if status == 'OK':
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    # Extract email details
                    subject = email_message.get('Subject', 'No Subject')
                    sender = email_message.get('From', 'Unknown Sender')
                    date_str = email_message.get('Date', '')
                    
                    # Parse date
                    try:
                        timestamp = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                    except:
                        timestamp = datetime.now()
                    
                    # Get email body
                    body = ""
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = email_message.get_payload(decode=True).decode()
                    
                    email_msg = EmailMessage(
                        subject=subject,
                        sender=sender,
                        recipient=self.email_address,
                        body=body[:200] + "..." if len(body) > 200 else body,
                        timestamp=timestamp,
                        message_id=email_id.decode()
                    )
                    
                    recent_emails.append(email_msg)
            
            mail.close()
            mail.logout()
            
            return recent_emails
            
        except Exception as e:
            self.logger.error(f"Error getting recent emails: {e}")
            return []
    
    async def send_email(self, to: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send an email"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_address
            msg['To'] = to
            msg['Subject'] = subject
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
            
            server.login(self.email_address, self.password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_address, to, text)
            server.quit()
            
            self.logger.info(f"Email sent to {to}: {subject}")
            
            # Emit email sent event
            self.emit_event("email_sent", {
                "to": to,
                "subject": subject
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return False
    
    def get_commands(self) -> List[str]:
        """Get supported commands"""
        return [
            "email",
            "mail",
            "e-posta",
            "check email",
            "email kontrol",
            "unread emails",
            "okunmamış e-postalar",
            "send email",
            "e-posta gönder",
            "new messages",
            "yeni mesajlar"
        ]
    
    def get_capabilities(self) -> List[str]:
        """Get plugin capabilities"""
        return [
            "email_reading",
            "email_sending",
            "unread_count",
            "email_notifications",
            "email_management"
        ]
