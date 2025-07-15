#!/usr/bin/env python3
"""
Python Script Runner
A simple script runner that can execute any Python script with the required libraries.
"""

from typing import List
import sys
from .base import PythonScriptRunnerTool
from kubiya_sdk.tools import Arg
from kubiya_sdk.tools.registry import tool_registry

class CLITools:
    """Python Script Runner tools for executing Python scripts with required libraries."""

    def __init__(self):
        """Initialize and register Python Script Runner tools."""
        try:
            tools = [
                self.run_python_script()
            ]
            
            for tool in tools:
                try:
                    tool_registry.register("python_script_runner", tool)
                    print(f"✅ Registered: {tool.name}")
                except Exception as e:
                    print(f"❌ Failed to register {tool.name}: {str(e)}", file=sys.stderr)
                    raise
        except Exception as e:
            print(f"❌ Failed to register Python Script Runner tools: {str(e)}", file=sys.stderr)
            raise

    def run_python_script(self) -> PythonScriptRunnerTool:
        """Execute Python scripts with automatic dependency installation."""
        return PythonScriptRunnerTool(
            name="python_script_runner",
            description="Execute Python scripts with automatic installation of common libraries (pandas, openpyxl, lxml, boto3). Provide the script path or script content to run.",
            content="""
            #!/bin/bash
            set -e
            
            # Parse arguments
            script_path="$script_path"
            script_content="$script_content"
            
            # Validate arguments
            if [ -z "$script_path" ] && [ -z "$script_content" ]; then
                echo "❌ Either script_path or script_content argument is required"
                echo ""
                echo "Usage examples:"
                echo "  - script_path: /path/to/your/script.py"
                echo "  - script_content: 'import pandas as pd; print(pd.__version__)'"
                echo ""
                echo "Pre-installed libraries:"
                echo "  - pandas: Data manipulation and analysis"
                echo "  - openpyxl: Excel file reading and writing"
                echo "  - lxml: XML and HTML processing"
                echo "  - boto3: AWS SDK for Python"
                exit 1
            fi
            
            # Install minimal system dependencies if needed
            echo "📦 Installing minimal system dependencies..."
            apt-get update >/dev/null 2>&1 || true
            apt-get install -y gcc >/dev/null 2>&1 || true
            
            # Install required Python packages
            echo "📦 Installing required Python packages..."
            
            # Upgrade pip to latest version
            echo "Upgrading pip..."
            pip install --upgrade pip >/dev/null 2>&1
            
            # Install packages using pre-compiled wheels when possible
            echo "Installing pandas..."
            pip install pandas >/dev/null 2>&1 || {
                echo "❌ Failed to install pandas"
                exit 1
            }
            echo "✅ pandas installed successfully"
            
            echo "Installing openpyxl..."
            pip install openpyxl >/dev/null 2>&1 || {
                echo "❌ Failed to install openpyxl"
                exit 1
            }
            echo "✅ openpyxl installed successfully"
            
            echo "Installing lxml..."
            pip install lxml >/dev/null 2>&1 || {
                echo "❌ Failed to install lxml"
                exit 1
            }
            echo "✅ lxml installed successfully"
            
            echo "Installing boto3..."
            pip install boto3 >/dev/null 2>&1 || {
                echo "❌ Failed to install boto3"
                exit 1
            }
            echo "✅ boto3 installed successfully"
            
            # Handle script execution
            if [ -n "$script_content" ]; then
                echo "🐍 Executing Python script from content..."
                echo ""
                
                # Create temporary script file using printf to handle special characters
                TEMP_SCRIPT="/tmp/temp_script.py"
                
                # Use printf to safely write script content to file
                printf '%s\n' "$script_content" > "$TEMP_SCRIPT"
                
                echo "Script content:"
                echo "==============="
                cat "$TEMP_SCRIPT"
                echo "==============="
                echo ""
                
                # Execute the script
                echo "📤 Output:"
                if python "$TEMP_SCRIPT"; then
                    echo ""
                    echo "✅ Script executed successfully"
                else
                    echo ""
                    echo "❌ Script execution failed"
                    exit 1
                fi
                
                # Clean up
                rm -f "$TEMP_SCRIPT"
                
            elif [ -n "$script_path" ]; then
                echo "🐍 Executing Python script: $script_path"
                
                # Check if script exists
                if [ ! -f "$script_path" ]; then
                    echo "❌ Error: Script '$script_path' not found."
                    exit 1
                fi
                
                # Execute the script
                echo "📤 Output:"
                if python "$script_path"; then
                    echo ""
                    echo "✅ Script executed successfully"
                else
                    echo ""
                    echo "❌ Script execution failed"
                    exit 1
                fi
            fi
            """,
            args=[
                Arg(name="script_path", description="Path to the Python script file to execute", required=False),
                Arg(name="script_content", description="Python script content to execute directly (alternative to script_path)", required=False)
            ]
        )


CLITools() 