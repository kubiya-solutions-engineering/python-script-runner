#!/usr/bin/env python3
"""
CodeSandbox SDK Runner
Tools for creating and executing Python scripts in CodeSandbox using the new SDK.
"""

from typing import List
import sys
from .codesandbox_base import CodeSandboxTool
from kubiya_sdk.tools import Arg
from kubiya_sdk.tools.registry import tool_registry

class CodeSandboxSDKTools:
    """CodeSandbox SDK tools for creating and executing scripts using the new SDK."""

    def __init__(self):
        """Initialize and register CodeSandbox SDK tools."""
        try:
            tools = [
                self.create_codesandbox_sdk(),
                self.execute_codesandbox_sdk()
            ]
            
            for tool in tools:
                try:
                    tool_registry.register("python_script_runner", tool)
                    print(f"✅ Registered: {tool.name}")
                except Exception as e:
                    print(f"❌ Failed to register {tool.name}: {str(e)}", file=sys.stderr)
                    raise
        except Exception as e:
            print(f"❌ Failed to register CodeSandbox SDK tools: {str(e)}", file=sys.stderr)
            raise

    def create_codesandbox_sdk(self) -> CodeSandboxTool:
        """Create a CodeSandbox using the new SDK."""
        return CodeSandboxTool(
            name="create_codesandbox_sdk",
            description="Create a CodeSandbox using the new CodeSandbox SDK. Requires CSB_API_KEY secret and a CodeSandbox Pro plan.",
            content="""
            # Create Node.js script to use the CodeSandbox SDK
            cat > /tmp/create_sandbox.js << 'EOF'
const { CodeSandbox } = require('@codesandbox/sdk');

async function createSandbox() {
    try {
        const sdk = new CodeSandbox(process.env.CSB_API_KEY);
        
        console.log('🚀 Creating CodeSandbox using SDK...');
        
        // Create the sandbox
        const sandbox = await sdk.sandboxes.create({
            title: process.env.SANDBOX_NAME || 'Python Script Sandbox',
            description: 'Python script created via CodeSandbox SDK',
            files: {
                'main.py': {
                    content: process.env.SCRIPT_CONTENT || 'print("Hello, CodeSandbox!")'
                },
                'requirements.txt': {
                    content: 'pandas\\nnumpy\\nrequests\\nboto3\\nopenpyxl\\nlxml'
                },
                'README.md': {
                    content: '# Python Script Sandbox\\n\\nThis sandbox contains a Python script created via the CodeSandbox SDK.\\n\\n## Usage\\n\\n1. Run the script: `python main.py`\\n2. Install dependencies: `pip install -r requirements.txt`\\n\\nHappy coding!'
                }
            },
            template: 'python'
        });
        
        console.log('\\n✅ CodeSandbox created successfully!');
        console.log('🆔 Sandbox ID:', sandbox.id);
        console.log('🌐 Sandbox URL:', sandbox.url);
        console.log('📝 Title:', sandbox.title);
        console.log('📄 Description:', sandbox.description);
        
        // Save sandbox info
        const fs = require('fs');
        const sandboxInfo = {
            id: sandbox.id,
            url: sandbox.url,
            title: sandbox.title,
            description: sandbox.description,
            createdAt: new Date().toISOString()
        };
        
        const filename = `/tmp/sandbox_${(process.env.SANDBOX_NAME || 'python-script').replace(/[^a-zA-Z0-9]/g, '_')}.json`;
        fs.writeFileSync(filename, JSON.stringify(sandboxInfo, null, 2));
        
        console.log('💾 Sandbox info saved to:', filename);
        console.log('');
        console.log('🎉 Your sandbox is ready!');
        console.log('You can now:');
        console.log('1. Visit the URL to see your sandbox');
        console.log('2. Use execute_codesandbox_sdk to run commands in this sandbox');
        console.log('3. Share the URL with others');
        
    } catch (error) {
        console.error('❌ Failed to create CodeSandbox:', error.message);
        
        if (error.message.includes('unauthorized') || error.message.includes('authentication')) {
            console.error('');
            console.error('🔑 Authentication Error:');
            console.error('1. Check that your CSB_API_KEY is correct');
            console.error('2. Ensure you have a CodeSandbox Pro plan');
            console.error('3. Verify the API key has the necessary permissions');
        } else if (error.message.includes('rate limit')) {
            console.error('');
            console.error('⏱️ Rate Limit Error:');
            console.error('You have exceeded the API rate limit. Please try again later.');
        }
        
        process.exit(1);
    }
}

createSandbox();
EOF
            
            # Export environment variables for the Node.js script
            export SCRIPT_CONTENT="$script_content"
            export SANDBOX_NAME="$sandbox_name"
            
            # Run the Node.js script
            echo "🔧 Running CodeSandbox SDK..."
            node /tmp/create_sandbox.js
            """,
            args=[
                Arg(name="script_content", description="Python script content to run in the CodeSandbox", required=True),
                Arg(name="sandbox_name", description="Name for the sandbox (default: Python Script Sandbox)", required=False)
            ]
        )

    def execute_codesandbox_sdk(self) -> CodeSandboxTool:
        """Execute a script in an existing CodeSandbox using the SDK."""
        return CodeSandboxTool(
            name="execute_codesandbox_sdk",
            description="Execute Python script in an existing CodeSandbox using the SDK. Can connect to existing sandbox or create a new one.",
            content="""
            # Create Node.js script to use the CodeSandbox SDK
            cat > /tmp/execute_sandbox.js << 'EOF'
const { CodeSandbox } = require('@codesandbox/sdk');
const fs = require('fs');
const path = require('path');

async function executeSandbox() {
    try {
        const sdk = new CodeSandbox(process.env.CSB_API_KEY);
        let sandboxId = process.env.SANDBOX_ID;
        
        // If no sandbox ID provided, try to find saved sandbox or create new one
        if (!sandboxId) {
            const sandboxName = process.env.SANDBOX_NAME || 'python-execution';
            const filename = `/tmp/sandbox_${sandboxName.replace(/[^a-zA-Z0-9]/g, '_')}.json`;
            
            // Try to load existing sandbox info
            if (fs.existsSync(filename)) {
                console.log('📂 Found saved sandbox info:', filename);
                try {
                    const sandboxInfo = JSON.parse(fs.readFileSync(filename, 'utf8'));
                    sandboxId = sandboxInfo.id;
                    console.log('🆔 Using existing sandbox:', sandboxId);
                } catch (e) {
                    console.log('⚠️  Could not read sandbox file:', e.message);
                }
            }
            
            // If still no sandbox ID, create a new one
            if (!sandboxId) {
                console.log('🏗️  No existing sandbox found, creating new one...');
                
                const sandbox = await sdk.sandboxes.create({
                    title: sandboxName,
                    description: 'Python execution sandbox created via SDK',
                    files: {
                        'main.py': {
                            content: process.env.SCRIPT_CONTENT || 'print("Hello, CodeSandbox!")'
                        },
                        'requirements.txt': {
                            content: 'pandas\\nnumpy\\nrequests\\nboto3\\nopenpyxl\\nlxml'
                        }
                    },
                    template: 'python'
                });
                
                sandboxId = sandbox.id;
                
                // Save sandbox info
                const sandboxInfo = {
                    id: sandbox.id,
                    url: sandbox.url,
                    title: sandbox.title,
                    description: sandbox.description,
                    createdAt: new Date().toISOString()
                };
                
                fs.writeFileSync(filename, JSON.stringify(sandboxInfo, null, 2));
                console.log('✅ New sandbox created:', sandboxId);
            }
        }
        
        // Connect to the sandbox
        console.log('🔗 Connecting to sandbox:', sandboxId);
        const sandbox = await sdk.sandboxes.get(sandboxId);
        const client = await sandbox.connect();
        
        console.log('✅ Connected to sandbox successfully!');
        
        // Execute the script
        console.log('▶️  Executing Python script...');
        const output = await client.commands.run('python main.py');
        
        console.log('\\n📤 Script Output:');
        console.log('================');
        console.log(output);
        console.log('================');
        
        console.log('\\n🎯 Execution Details:');
        console.log('📍 Sandbox URL:', sandbox.url);
        console.log('🆔 Sandbox ID:', sandbox.id);
        console.log('📝 Title:', sandbox.title);
        
        console.log('\\n✅ Script executed successfully!');
        
    } catch (error) {
        console.error('❌ Failed to execute in CodeSandbox:', error.message);
        
        if (error.message.includes('unauthorized') || error.message.includes('authentication')) {
            console.error('');
            console.error('🔑 Authentication Error:');
            console.error('1. Check that your CSB_API_KEY is correct');
            console.error('2. Ensure you have a CodeSandbox Pro plan');
            console.error('3. Verify the API key has the necessary permissions');
        } else if (error.message.includes('not found')) {
            console.error('');
            console.error('🔍 Sandbox Not Found:');
            console.error('The specified sandbox ID may not exist or you may not have access to it.');
        }
        
        process.exit(1);
    }
}

executeSandbox();
EOF
            
            # Export environment variables for the Node.js script
            export SCRIPT_CONTENT="$script_content"
            export SANDBOX_ID="$sandbox_id"
            export SANDBOX_NAME="$sandbox_name"
            
            # Run the Node.js script
            echo "🔧 Running CodeSandbox SDK execution..."
            node /tmp/execute_sandbox.js
            """,
            args=[
                Arg(name="script_content", description="Python script content to execute", required=True),
                Arg(name="sandbox_id", description="Existing CodeSandbox ID (optional)", required=False),
                Arg(name="sandbox_name", description="Sandbox name to find or create (default: python-execution)", required=False)
            ]
        )


# Initialize the tools
CodeSandboxSDKTools() 