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
            cat > /tmp/codesandbox_project/create_sandbox.js << 'EOF'
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
            
            # Run the Node.js script from the correct directory
            echo "🔧 Running CodeSandbox SDK..."
            cd /tmp/codesandbox_project
            node create_sandbox.js
            """,
            args=[
                Arg(name="script_content", description="Python script content to run in the CodeSandbox", required=True),
                Arg(name="sandbox_name", description="Name for the sandbox (default: Python Script Sandbox)", required=False)
            ]
        )

    def execute_codesandbox_sdk(self) -> CodeSandboxTool:
        """Execute a script in a CodeSandbox using the SDK."""
        return CodeSandboxTool(
            name="execute_codesandbox_sdk",
            description="Execute Python script in CodeSandbox using the SDK. Can resume existing sandbox or create a new one.",
            content="""
            # Create Node.js script to use the CodeSandbox SDK
            cat > /tmp/codesandbox_project/execute_sandbox.js << 'EOF'
const { CodeSandbox } = require('@codesandbox/sdk');
const fs = require('fs');

async function executeSandbox() {
    try {
        const sdk = new CodeSandbox(process.env.CSB_API_KEY);
        let sandbox;
        
        // Check if we should try to resume an existing sandbox
        const sandboxId = process.env.SANDBOX_ID;
        if (sandboxId) {
            console.log(`🔄 Attempting to resume existing sandbox: ${sandboxId}`);
            try {
                sandbox = await sdk.sandboxes.resume(sandboxId);
                console.log('✅ Successfully resumed existing sandbox!');
            } catch (resumeError) {
                console.log(`⚠️  Failed to resume sandbox: ${resumeError.message}`);
                console.log('🏗️  Creating new sandbox instead...');
                sandbox = null;
            }
        }
        
        // Create a new sandbox if we don't have one
        if (!sandbox) {
            console.log('🚀 Creating new CodeSandbox environment...');
            
            sandbox = await sdk.sandboxes.create({
                title: process.env.SANDBOX_NAME || 'Python Script Execution',
                description: 'Python script execution via CodeSandbox SDK',
                files: {
                    'main.py': {
                        content: process.env.SCRIPT_CONTENT || 'print("Hello, CodeSandbox!")'
                    },
                    'requirements.txt': {
                        content: 'pandas\\nnumpy\\nrequests\\nboto3\\nopenpyxl\\nlxml'
                    }
                },
                template: 'python',
                privacy: 'unlisted', // Make it accessible by URL but not public
                hibernationTimeoutSeconds: 1800 // 30 minutes before hibernation
            });
            
            console.log('✅ Sandbox created successfully!');
        }
        
        console.log('🆔 Sandbox ID:', sandbox.id);
        console.log('🌐 Sandbox URL:', `https://codesandbox.io/s/${sandbox.id}`);
        console.log('🔧 Bootup Type:', sandbox.bootupType);
        console.log('🏢 Cluster:', sandbox.cluster);
        
        // Connect to the sandbox with a session
        console.log('🔗 Connecting to sandbox...');
        const client = await sandbox.connect({
            id: 'script-executor', // Session ID
            permission: 'write' // Need write access to execute commands
        });
        
        console.log('✅ Connected to sandbox successfully!');
        
        // Check if we need to install dependencies (for new sandboxes)
        if (!sandboxId || sandbox.bootupType === 'CLEAN') {
            console.log('📦 Installing Python dependencies...');
            try {
                await client.commands.run('pip install pandas numpy requests boto3 openpyxl lxml', {
                    timeout: 120000 // 2 minutes timeout
                });
                console.log('✅ Dependencies installed successfully!');
            } catch (installError) {
                console.log(`⚠️  Dependency installation warning: ${installError.message}`);
                console.log('Continuing with execution...');
            }
        } else {
            console.log('📦 Dependencies should already be installed (resumed sandbox)');
        }
        
        // Execute the script
        console.log('▶️  Executing Python script...');
        const output = await client.commands.run('python main.py', {
            timeout: 300000 // 5 minutes timeout for script execution
        });
        
        console.log('\\n📤 Script Output:');
        console.log('================');
        console.log(output);
        console.log('================');
        
        console.log('\\n🎯 Execution Details:');
        console.log('📍 Sandbox URL:', `https://codesandbox.io/s/${sandbox.id}`);
        console.log('🆔 Sandbox ID:', sandbox.id);
        console.log('📝 Title:', sandbox.title || 'Untitled');
        console.log('🔧 Up to Date:', sandbox.isUpToDate);
        
        // Save sandbox info for future use
        const sandboxInfo = {
            id: sandbox.id,
            url: `https://codesandbox.io/s/${sandbox.id}`,
            title: sandbox.title || 'Untitled',
            description: sandbox.description || '',
            cluster: sandbox.cluster,
            bootupType: sandbox.bootupType,
            isUpToDate: sandbox.isUpToDate,
            createdAt: new Date().toISOString()
        };
        
        const filename = `/tmp/sandbox_execution_${Date.now()}.json`;
        fs.writeFileSync(filename, JSON.stringify(sandboxInfo, null, 2));
        console.log('💾 Sandbox info saved to:', filename);
        
        console.log('\\n✅ Script executed successfully!');
        console.log('💡 Tip: Use the same sandbox ID to resume this environment later');
        
    } catch (error) {
        console.error('❌ Failed to execute in CodeSandbox:', error.message);
        console.error('Full error:', error);
        
        if (error.message.includes('unauthorized') || error.message.includes('authentication')) {
            console.error('');
            console.error('🔑 Authentication Error:');
            console.error('1. Check that your CSB_API_KEY is correct');
            console.error('2. Ensure you have a CodeSandbox Pro plan');
            console.error('3. Verify the API key has the necessary permissions');
            console.error('4. Get your API key from: https://codesandbox.io/dashboard/settings');
        } else if (error.message.includes('rate limit')) {
            console.error('');
            console.error('⏱️ Rate Limit Error:');
            console.error('You have exceeded the API rate limit. Please try again later.');
        } else if (error.message.includes('timeout')) {
            console.error('');
            console.error('⏱️ Timeout Error:');
            console.error('The operation took too long. Consider breaking down the script or increasing timeout.');
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
            
            # Run the Node.js script from the correct directory
            echo "🔧 Running CodeSandbox SDK execution..."
            cd /tmp/codesandbox_project
            node execute_sandbox.js
            """,
            args=[
                Arg(name="script_content", description="Python script content to execute", required=True),
                Arg(name="sandbox_id", description="Existing sandbox ID to resume (optional)", required=False),
                Arg(name="sandbox_name", description="Sandbox name (default: Python Script Execution)", required=False)
            ]
        )


# Initialize the tools
CodeSandboxSDKTools() 