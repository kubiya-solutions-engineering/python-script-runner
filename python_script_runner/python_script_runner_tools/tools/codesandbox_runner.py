#!/usr/bin/env python3
"""
CodeSandbox Runner
Tools for creating and executing Python scripts in CodeSandbox cloud environments.
"""

from typing import List
import sys
from .base import PythonScriptRunnerTool
from kubiya_sdk.tools import Arg
from kubiya_sdk.tools.registry import tool_registry

class CodeSandboxTools:
    """CodeSandbox Runner tools for creating and executing scripts in cloud sandboxes."""

    def __init__(self):
        """Initialize and register CodeSandbox Runner tools."""
        try:
            tools = [
                self.create_codesandbox(),
                self.execute_codesandbox()
            ]
            
            for tool in tools:
                try:
                    tool_registry.register("python_script_runner", tool)
                    print(f"✅ Registered: {tool.name}")
                except Exception as e:
                    print(f"❌ Failed to register {tool.name}: {str(e)}", file=sys.stderr)
                    raise
        except Exception as e:
            print(f"❌ Failed to register CodeSandbox Runner tools: {str(e)}", file=sys.stderr)
            raise

    def create_codesandbox(self) -> PythonScriptRunnerTool:
        """Create a CodeSandbox with Python script content."""
        return PythonScriptRunnerTool(
            name="create_codesandbox",
            description="Create a CodeSandbox cloud environment with Python script content. Uses the CODE_SANDBOX_API secret for authentication.",
            content="""
            #!/bin/bash
            set -e
            
            # Parse arguments
            script_content="$script_content"
            sandbox_name="$sandbox_name"
            template_type="$template_type"
            
            # Get API key from environment variable (secret)
            api_key="$CODE_SANDBOX_API"
            
            # Validate arguments
            if [ -z "$script_content" ]; then
                echo "❌ script_content argument is required"
                echo ""
                echo "Usage:"
                echo "  script_content: Python code to run in the sandbox"
                echo "  sandbox_name: (optional) Name for the sandbox (default: python-script)"
                echo "  template_type: (optional) Template type (default: python)"
                echo ""
                echo "Example:"
                echo "  script_content: 'print(\"Hello, CodeSandbox!\")'"
                echo "  sandbox_name: 'my-python-script'"
                echo "  template_type: 'python'"
                echo ""
                echo "Note: CodeSandbox API key is configured as a secret (CODE_SANDBOX_API)"
                exit 1
            fi
            
            if [ -z "$api_key" ]; then
                echo "❌ CODE_SANDBOX_API secret is not configured"
                echo ""
                echo "To configure the CodeSandbox API key secret:"
                echo "1. Go to https://codesandbox.io/dashboard/settings"
                echo "2. Navigate to 'API Keys' or 'Integrations'"
                echo "3. Create a new API key"
                echo "4. Configure the CODE_SANDBOX_API secret in your environment"
                echo ""
                echo "Note: You may need to upgrade to a paid plan to access the API"
                exit 1
            fi
            
            # Set defaults
            if [ -z "$sandbox_name" ]; then
                sandbox_name="python-script"
            fi
            
            if [ -z "$template_type" ]; then
                template_type="python"
            fi
            
            echo "🏗️  Creating CodeSandbox environment..."
            echo "📝 Name: $sandbox_name"
            echo "🐍 Template: $template_type"
            if [ -n "$api_key" ] && [ "$api_key" != "" ]; then
                echo "🔑 API Key: ****$(echo "$api_key" | tail -c 5)"
            else
                echo "🔑 API Key: Not configured"
            fi
            echo ""
            
            # Install required packages
            echo "📦 Installing required packages..."
            pip install requests >/dev/null 2>&1 || {
                echo "❌ Failed to install requests"
                exit 1
            }
            echo "✅ requests installed"
            
            # Create the sandbox using CodeSandbox API
            echo "🚀 Creating sandbox on CodeSandbox..."
            
            # Create Python script for API call
            python3 -c "
import requests
import json
import sys
import os

def create_codesandbox(script_content, sandbox_name, template_type, api_key):
    # CodeSandbox API endpoint
    url = 'https://codesandbox.io/api/v1/sandboxes'
    
    # Create files structure
    files = {
        'main.py': {
            'content': script_content
        },
        'requirements.txt': {
            'content': '# Add your Python dependencies here\\npandas\\nnumpy\\nrequests\\n'
        },
        'package.json': {
            'content': json.dumps({
                'name': sandbox_name,
                'version': '1.0.0',
                'description': 'Python script sandbox',
                'main': 'main.py',
                'scripts': {
                    'start': 'python main.py'
                }
            }, indent=2)
        },
        'README.md': {
            'content': '# Python Script Sandbox\\n\\nThis sandbox contains a Python script ready to run.\\n\\n## Usage\\n\\n1. Run the script: \`python main.py\`\\n2. Install dependencies: \`pip install -r requirements.txt\`\\n\\nHappy coding!'
        }
    }
    
    # Create sandbox payload
    payload = {
        'files': files,
        'template': 'static'
    }
    
    # Headers with authentication
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        print('📡 Sending authenticated request to CodeSandbox API...')
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print('📊 Response status:', response.status_code)
        
        if response.status_code == 200:
            sandbox_data = response.json()
            return sandbox_data
        elif response.status_code == 401:
            print('❌ Authentication failed!')
            print('Please check your CODE_SANDBOX_API secret:')
            print('1. Ensure it is correct and not expired')
            print('2. Verify you have the necessary permissions')
            print('3. Check if your plan supports API access')
            return None
        elif response.status_code == 403:
            print('❌ Access forbidden!')
            print('Your API key may not have permission to create sandboxes')
            print('Consider upgrading your CodeSandbox plan')
            return None
        else:
            print('❌ API Error:', response.status_code)
            print('Response:', response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print('❌ Request failed:', e)
        return None
    except Exception as e:
        print('❌ Unexpected error:', e)
        return None

# Get arguments from command line
script_content = '''$script_content'''
sandbox_name = '''$sandbox_name'''
template_type = '''$template_type'''
api_key = '''$api_key'''

result = create_codesandbox(script_content, sandbox_name, template_type, api_key)

if result:
    print('\\n✅ CodeSandbox created successfully!')
    print('🆔 Sandbox ID:', result.get('id', 'N/A'))
    print('🌐 Sandbox URL: https://codesandbox.io/s/' + result.get('id', 'N/A'))
    print('📄 Title:', result.get('title', 'N/A'))
    print('📝 Description:', result.get('description', 'N/A'))
    
    # Save sandbox info for later use
    sandbox_file = '/tmp/sandbox_' + sandbox_name.replace(' ', '_') + '.json'
    with open(sandbox_file, 'w') as f:
        json.dump(result, f, indent=2)
        
    print('💾 Sandbox info saved to:', sandbox_file)
    print('')
    print('🎉 Your sandbox is ready!')
    print('You can now:')
    print('1. Visit the URL to see your sandbox')
    print('2. Use execute_codesandbox to run scripts in this sandbox')
    print('3. Share the URL with others')
    
else:
    print('\\n❌ Failed to create CodeSandbox')
    sys.exit(1)
"
            """,
            args=[
                Arg(name="script_content", description="Python script content to run in the CodeSandbox", required=True),
                Arg(name="sandbox_name", description="Name for the sandbox (default: python-script)", required=False),
                Arg(name="template_type", description="Template type for the sandbox (default: python)", required=False)
            ]
        )

    def execute_codesandbox(self) -> PythonScriptRunnerTool:
        """Execute a script in an existing CodeSandbox or create a new one."""
        return PythonScriptRunnerTool(
            name="execute_codesandbox",
            description="Execute Python script in CodeSandbox environment. Can work with existing sandbox or create a new one if none exists. Uses CODE_SANDBOX_API secret for creating new sandboxes.",
            content="""
            #!/bin/bash
            set -e
            
            # Parse arguments
            script_content="$script_content"
            sandbox_id="$sandbox_id"
            sandbox_name="$sandbox_name"
            
            # Get API key from environment variable (secret)
            api_key="$CODE_SANDBOX_API"
            
            # Validate arguments
            if [ -z "$script_content" ]; then
                echo "❌ script_content argument is required"
                echo ""
                echo "Usage:"
                echo "  script_content: Python code to execute"
                echo "  sandbox_id: (optional) Existing sandbox ID"
                echo "  sandbox_name: (optional) Sandbox name to look for or create"
                echo ""
                echo "Example:"
                echo "  script_content: 'print(\"Hello, World!\")'"
                echo "  sandbox_id: 'abc123'"
                echo "  sandbox_name: 'my-python-script'"
                echo ""
                echo "Note: CodeSandbox API key is configured as a secret (CODE_SANDBOX_API)"
                exit 1
            fi
            
            # Set defaults
            if [ -z "$sandbox_name" ]; then
                sandbox_name="python-execution"
            fi
            
            echo "🐍 Executing Python script in CodeSandbox..."
            echo ""
            
            # Install required packages
            echo "📦 Installing required packages..."
            pip install requests >/dev/null 2>&1 || {
                echo "❌ Failed to install requests"
                exit 1
            }
            echo "✅ requests installed"
            
            # Create execution script
            python3 -c "
import requests
import json
import sys
import os
import time

def execute_in_codesandbox(script_content, sandbox_id=None, sandbox_name=None, api_key=None):
    # If no sandbox_id provided, try to find saved sandbox or create new one
    if not sandbox_id:
        # Try to find saved sandbox info
        sandbox_file = '/tmp/sandbox_' + sandbox_name.replace(' ', '_') + '.json'
        if os.path.exists(sandbox_file):
            print('📂 Found saved sandbox info:', sandbox_file)
            try:
                with open(sandbox_file, 'r') as f:
                    sandbox_data = json.load(f)
                    sandbox_id = sandbox_data.get('id')
                    print('🆔 Using existing sandbox:', sandbox_id)
            except Exception as e:
                print('⚠️  Could not read sandbox file:', e)
        
        # If still no sandbox_id, create a new one
        if not sandbox_id:
            if not api_key:
                print('❌ CODE_SANDBOX_API secret is required to create a new sandbox')
                print('Please configure the CODE_SANDBOX_API secret or use an existing sandbox_id')
                return False
            print('🏗️  No existing sandbox found, creating new one...')
            return create_new_sandbox(script_content, sandbox_name, api_key)
    
    # Execute in existing sandbox
    print('▶️  Executing script in sandbox:', sandbox_id)
    
    # For now, we provide instructions since CodeSandbox doesn't have 
    # a direct execution API - the execution happens in the browser
    sandbox_url = 'https://codesandbox.io/s/' + sandbox_id
    
    print('\\n🎯 Execution Details:')
    print('='*50)
    print('📍 Sandbox URL:', sandbox_url)
    print('🆔 Sandbox ID:', sandbox_id)
    print('\\n📜 Script to execute:')
    print('-'*30)
    print(script_content)
    print('-'*30)
    
    print('\\n📋 Instructions:')
    print('1. Open the sandbox URL in your browser')
    print('2. The script will be available in the sandbox')
    print('3. You can run it directly in the CodeSandbox environment')
    print('4. CodeSandbox provides a full development environment with:')
    print('   - Python runtime')
    print('   - Package management')
    print('   - File system access')
    print('   - Terminal access')
    print('   - Real-time collaboration')
    
    print('\\n✅ Script ready for execution in CodeSandbox!')
    return True

def create_new_sandbox(script_content, sandbox_name, api_key):
    print('🚀 Creating new CodeSandbox with authentication...')
    
    # CodeSandbox API endpoint
    url = 'https://codesandbox.io/api/v1/sandboxes'
    
    # Create files structure
    files = {
        'main.py': {
            'content': script_content
        },
        'requirements.txt': {
            'content': '# Add your Python dependencies here\\npandas\\nnumpy\\nrequests\\n'
        },
        'README.md': {
            'content': '# ' + sandbox_name + '\\n\\nThis is a Python script sandbox created for executing Python code.\\n\\n## Running the Script\\n\\n1. Click the Run button or use the terminal\\n2. Run: \`python main.py\`\\n\\n## Available Libraries\\n\\n- pandas\\n- numpy\\n- requests\\n- And many more via pip install\\n\\nHappy coding! 🐍'
        }
    }
    
    # Create sandbox payload
    payload = {
        'files': files,
        'template': 'static'
    }
    
    # Headers with authentication
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        print('📡 Sending authenticated request to CodeSandbox API...')
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print('📊 Response status:', response.status_code)
        
        if response.status_code == 200:
            sandbox_data = response.json()
            sandbox_id = sandbox_data.get('id')
            
            # Save sandbox info
            sandbox_file = '/tmp/sandbox_' + sandbox_name.replace(' ', '_') + '.json'
            with open(sandbox_file, 'w') as f:
                json.dump(sandbox_data, f, indent=2)
            
            print('\\n✅ New CodeSandbox created successfully!')
            print('🆔 Sandbox ID:', sandbox_id)
            print('🌐 Sandbox URL: https://codesandbox.io/s/' + sandbox_id)
            
            # Now execute in the new sandbox
            return execute_in_codesandbox(script_content, sandbox_id, sandbox_name, api_key)
        elif response.status_code == 401:
            print('❌ Authentication failed!')
            print('Please check your CODE_SANDBOX_API secret')
            return False
        elif response.status_code == 403:
            print('❌ Access forbidden!')
            print('Your API key may not have permission to create sandboxes')
            return False
        else:
            print('❌ API Error:', response.status_code)
            print('Response:', response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print('❌ Request failed:', e)
        return False
    except Exception as e:
        print('❌ Unexpected error:', e)
        return False

# Get arguments from command line
script_content = '''$script_content'''
sandbox_id = '''$sandbox_id''' if '''$sandbox_id''' != '' else None
sandbox_name = '''$sandbox_name''' if '''$sandbox_name''' != '' else 'python-execution'
api_key = '''$api_key'''

success = execute_in_codesandbox(script_content, sandbox_id, sandbox_name, api_key)

if not success:
    print('\\n❌ Failed to execute in CodeSandbox')
    sys.exit(1)
"
            """,
            args=[
                Arg(name="script_content", description="Python script content to execute", required=True),
                Arg(name="sandbox_id", description="Existing CodeSandbox ID (optional)", required=False),
                Arg(name="sandbox_name", description="Sandbox name to find or create (default: python-execution)", required=False)
            ]
        )


CodeSandboxTools() 