#!/usr/bin/env python3
"""
Test AI Command Logging System
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from features.command_processing.ai_command_logger import get_ai_logger, LogLevel

async def test_ai_logging():
    """Test AI command logging functionality"""
    
    print("🧪 Testing AI Command Logging System...")
    
    # Get logger instance
    ai_logger = get_ai_logger()
    
    # Test successful command
    print("\n✅ Testing successful command logging...")
    ai_logger.log_command(
        command_id="test-001",
        command_text="yaz Merhaba dünya",
        command_type="quick",
        success=True,
        log_level=LogLevel.SUCCESS,
        execution_time=0.5,
        capabilities_used=["text_input"],
        steps_executed=["Extracted text", "Typed text"],
        context={"matched_keyword": "yaz", "priority": 100}
    )
    
    # Test failed command
    print("❌ Testing failed command logging...")
    ai_logger.log_command(
        command_id="test-002",
        command_text="yaz Türkiye'nin başkenti neresidir",
        command_type="quick",
        success=False,
        log_level=LogLevel.ERROR,
        error_message="Capability not found: text_input",
        execution_time=0.2,
        capabilities_used=["text_input"],
        steps_failed=["Failed to find text_input capability"],
        improvement_suggestions=["Fix capability registration", "Add error handling"],
        context={"matched_keyword": "yaz", "priority": 100}
    )
    
    # Test intelligent command
    print("🤖 Testing intelligent command logging...")
    ai_logger.log_command(
        command_id="test-003",
        command_text="Find music on YouTube and play it",
        command_type="intelligent",
        success=True,
        log_level=LogLevel.SUCCESS,
        execution_time=2.5,
        capabilities_used=["youtube_search", "youtube_automation"],
        steps_executed=["Search YouTube", "Select video", "Play video"],
        context={"complexity": "moderate", "ai_confidence": 0.85}
    )
    
    # Generate analysis report
    print("\n📊 Generating analysis report...")
    report = ai_logger.generate_analysis_report()
    
    print(f"Total commands: {report['summary']['total_commands']}")
    print(f"Success rate: {report['summary']['success_rate']}%")
    print(f"Error patterns: {report['error_patterns']}")
    print(f"Improvement suggestions: {report['improvement_suggestions']}")
    
    # Export analysis
    ai_logger.export_analysis("data/logs/test_ai_analysis.json")
    print("📁 Analysis exported to data/logs/test_ai_analysis.json")
    
    print("\n✅ AI Command Logging Test Completed!")

if __name__ == "__main__":
    asyncio.run(test_ai_logging())
