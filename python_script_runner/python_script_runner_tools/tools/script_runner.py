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
            #!/bin/sh
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
            
            # Install system dependencies
            echo "📦 Installing system dependencies..."
            apk add --no-cache python3 python3-dev py3-pip gcc musl-dev libxml2-dev libxslt-dev >/dev/null 2>&1 || {
                echo "❌ Failed to install system dependencies"
                exit 1
            }
            
            # Install required Python packages
            echo "📦 Installing required Python packages..."
            REQUIRED_PACKAGES="pandas openpyxl lxml boto3"
            
            for package in $REQUIRED_PACKAGES; do
                echo "Installing $package..."
                if pip3 install "$package" >/dev/null 2>&1; then
                    echo "✅ $package installed successfully"
                else
                    echo "❌ Failed to install $package"
                    exit 1
                fi
            done
            
            # Handle script execution
            if [ -n "$script_content" ]; then
                echo "🐍 Executing Python script from content..."
                echo ""
                echo "Script content:"
                echo "==============="
                echo "$script_content"
                echo "==============="
                echo ""
                
                # Create temporary script file
                TEMP_SCRIPT="/tmp/temp_script.py"
                echo "$script_content" > "$TEMP_SCRIPT"
                
                # Execute the script
                echo "📤 Output:"
                if python3 "$TEMP_SCRIPT"; then
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
                if python3 "$script_path"; then
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
            ],
            image="alpine:latest"
        )


CLITools() 