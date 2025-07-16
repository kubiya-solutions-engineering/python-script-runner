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
        """Create a CodeSandbox using the new SDK and save the script file."""
        return CodeSandboxTool(
            name="create_codesandbox_sdk",
            description="Create a CodeSandbox using the new CodeSandbox SDK and save the Python script file. Requires CSB_API_KEY secret and a CodeSandbox Pro plan.",
            content="""
            # Create Node.js script to use the CodeSandbox SDK
            cat > /tmp/codesandbox_project/create_sandbox.js << 'EOF'
const { CodeSandbox } = require('@codesandbox/sdk');

// Helper function to add delays between logs for cleaner output
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function createSandbox() {
    try {
        const sdk = new CodeSandbox(process.env.CSB_API_KEY);
        
        console.log('🚀 Creating CodeSandbox using SDK...');
        await sleep(100);
        
        // Create the sandbox
        const sandbox = await sdk.sandboxes.create({
            title: process.env.SANDBOX_NAME || 'Python Script Sandbox',
            description: 'Python script created via CodeSandbox SDK',
            files: {
                'requirements.txt': {
                    content: 'pandas\\nnumpy\\nrequests\\nboto3\\nopenpyxl\\nlxml'
                },
                'README.md': {
                    content: '# Python Script Sandbox\\n\\nThis sandbox contains a Python script created via the CodeSandbox SDK.\\n\\n## Usage\\n\\n1. Run the script: `python main.py`\\n2. Install dependencies: `pip install -r requirements.txt`\\n\\nHappy coding!'
                }
            },
            template: 'python',
            privacy: 'unlisted',
            hibernationTimeoutSeconds: 1800
        });
        
        console.log('✅ CodeSandbox created successfully!');
        await sleep(100);
        console.log('🆔 Sandbox ID:', sandbox.id);
        await sleep(100);
        console.log('🌐 Sandbox URL:', `https://codesandbox.io/s/${sandbox.id}`);
        await sleep(100);
        
        // Connect to the sandbox to save the script file
        console.log('🔗 Connecting to sandbox to save script...');
        await sleep(100);
        const client = await sandbox.connect({
            id: 'script-creator',
            permission: 'write'
        });
        
        console.log('✅ Connected to sandbox successfully!');
        await sleep(100);
        
        // Save the script file using the proper file system API
        console.log('📝 Saving Python script to main.py...');
        await sleep(100);
        
        try {
            await client.fs.writeTextFile('main.py', process.env.SCRIPT_CONTENT || 'print("Hello, CodeSandbox!")');
            console.log('✅ Script saved to main.py successfully!');
            await sleep(100);
        } catch (saveError) {
            console.error('❌ Failed to save script:', saveError.message);
            await sleep(100);
            throw saveError;
        }
        
        // List files to confirm
        console.log('📂 Checking saved files...');
        await sleep(100);
        
        try {
            const files = await client.fs.readdir('.');
            console.log('Files in workspace:', files);
            await sleep(100);
        } catch (listError) {
            console.log('⚠️  Could not list files:', listError.message);
            await sleep(100);
        }
        
        // Save sandbox info
        const fs = require('fs');
        const sandboxInfo = {
            id: sandbox.id,
            url: `https://codesandbox.io/s/${sandbox.id}`,
            title: sandbox.title,
            description: sandbox.description,
            createdAt: new Date().toISOString()
        };
        
        const filename = `/tmp/sandbox_${(process.env.SANDBOX_NAME || 'python-script').replace(/[^a-zA-Z0-9]/g, '_')}.json`;
        fs.writeFileSync(filename, JSON.stringify(sandboxInfo, null, 2));
        
        console.log('💾 Sandbox info saved to:', filename);
        await sleep(100);
        console.log('');
        await sleep(100);
        console.log('🎉 Your sandbox is ready!');
        await sleep(100);
        console.log('You can now:');
        await sleep(100);
        console.log('1. Visit the URL to see your sandbox');
        await sleep(100);
        console.log('2. Use execute_codesandbox_sdk to run the script');
        await sleep(100);
        console.log('3. Share the URL with others');
        await sleep(100);
        
        // Exit successfully
        process.exit(0);
        
    } catch (error) {
        console.error('❌ Failed to create CodeSandbox:', error.message);
        await sleep(100);
        
        if (error.message.includes('unauthorized') || error.message.includes('authentication')) {
            console.error('');
            await sleep(100);
            console.error('🔑 Authentication Error:');
            await sleep(100);
            console.error('1. Check that your CSB_API_KEY is correct');
            await sleep(100);
            console.error('2. Ensure you have a CodeSandbox Pro plan');
            await sleep(100);
            console.error('3. Verify the API key has the necessary permissions');
            await sleep(100);
        } else if (error.message.includes('rate limit')) {
            console.error('');
            await sleep(100);
            console.error('⏱️ Rate Limit Error:');
            await sleep(100);
            console.error('You have exceeded the API rate limit. Please try again later.');
            await sleep(100);
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
                Arg(name="script_content", description="Python script content to save in the CodeSandbox", required=True),
                Arg(name="sandbox_name", description="Name for the sandbox (default: Python Script Sandbox)", required=False)
            ]
        )

    def execute_codesandbox_sdk(self) -> CodeSandboxTool:
        """Execute the existing Python script in a CodeSandbox using the SDK."""
        return CodeSandboxTool(
            name="execute_codesandbox_sdk",
            description="Execute the existing Python script (main.py) in a CodeSandbox using the SDK. Requires an existing sandbox ID.",
            content="""
            # Create Node.js script to use the CodeSandbox SDK
            cat > /tmp/codesandbox_project/execute_sandbox.js << 'EOF'
const { CodeSandbox } = require('@codesandbox/sdk');
const fs = require('fs');

// Helper function to add delays between logs for cleaner output
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function executeSandbox() {
    try {
        const sdk = new CodeSandbox(process.env.CSB_API_KEY);
        
        const sandboxId = process.env.SANDBOX_ID;
        if (!sandboxId) {
            throw new Error('SANDBOX_ID is required. Please provide the ID of an existing sandbox.');
        }
        
        console.log(`🔄 Connecting to existing sandbox: ${sandboxId}`);
        await sleep(100);
        
        // Resume the existing sandbox
        const sandbox = await sdk.sandboxes.resume(sandboxId);
        console.log('✅ Successfully connected to existing sandbox!');
        await sleep(100);
        
        console.log('🆔 Sandbox ID:', sandbox.id);
        await sleep(100);
        console.log('🌐 Sandbox URL:', `https://codesandbox.io/s/${sandbox.id}`);
        await sleep(100);
        console.log('📝 Title:', sandbox.title || 'Untitled');
        await sleep(100);
        console.log('🔧 Bootup Type:', sandbox.bootupType);
        await sleep(100);
        
        // Connect to the sandbox with a session
        console.log('🔗 Connecting to sandbox...');
        await sleep(100);
        const client = await sandbox.connect({
            id: 'script-executor',
            permission: 'write'
        });
        
        console.log('✅ Connected to sandbox successfully!');
        await sleep(100);
        
        // Check what files exist in the workspace
        console.log('📂 Checking workspace files...');
        await sleep(100);
        try {
            const files = await client.fs.readdir('.');
            console.log('Files in workspace:', files);
            await sleep(100);
        } catch (dirError) {
            console.log('Could not list files:', dirError.message);
            await sleep(100);
        }
        
        // Check if main.py exists
        let scriptExists = false;
        try {
            const scriptContent = await client.fs.readTextFile('main.py');
            console.log('✅ main.py exists and contains:', scriptContent.length, 'characters');
            await sleep(100);
            scriptExists = true;
        } catch (readError) {
            console.log('❌ main.py does not exist:', readError.message);
            await sleep(100);
            
            // Only create main.py if script_content is provided as fallback
            if (process.env.SCRIPT_CONTENT) {
                console.log('📝 Creating main.py from provided script content...');
                await sleep(100);
                await client.fs.writeTextFile('main.py', process.env.SCRIPT_CONTENT);
                console.log('✅ main.py created successfully!');
                await sleep(100);
                scriptExists = true;
            } else {
                throw new Error('main.py not found and no script_content provided. Please create the sandbox first or provide script_content as fallback.');
            }
        }
        
        if (!scriptExists) {
            throw new Error('No Python script found to execute.');
        }
        
        // Install dependencies if needed (for clean boots)
        if (sandbox.bootupType === 'CLEAN') {
            console.log('📦 Installing Python dependencies...');
            await sleep(100);
            try {
                await client.commands.run('pip install -r requirements.txt', {
                    timeout: 120000
                });
                console.log('✅ Dependencies installed successfully!');
                await sleep(100);
            } catch (installError) {
                console.log(`⚠️  Dependency installation warning: ${installError.message}`);
                await sleep(100);
                console.log('Continuing with execution...');
                await sleep(100);
            }
        } else {
            console.log('📦 Dependencies should already be installed (warm boot)');
            await sleep(100);
        }
        
        // Execute the script
        console.log('▶️  Executing Python script (main.py)...');
        await sleep(100);
        const output = await client.commands.run('python main.py', {
            timeout: 300000 // 5 minutes timeout
        });
        
        console.log('\\n📤 Script Output:');
        await sleep(100);
        console.log('================');
        await sleep(100);
        console.log(output);
        await sleep(100);
        console.log('================');
        await sleep(100);
        
        console.log('\\n🎯 Execution Details:');
        await sleep(100);
        console.log('📍 Sandbox URL:', `https://codesandbox.io/s/${sandbox.id}`);
        await sleep(100);
        console.log('🆔 Sandbox ID:', sandbox.id);
        await sleep(100);
        console.log('📝 Title:', sandbox.title || 'Untitled');
        await sleep(100);
        console.log('🔧 Up to Date:', sandbox.isUpToDate);
        await sleep(100);
        
        // Save execution info
        const executionInfo = {
            sandboxId: sandbox.id,
            url: `https://codesandbox.io/s/${sandbox.id}`,
            title: sandbox.title || 'Untitled',
            executedAt: new Date().toISOString(),
            bootupType: sandbox.bootupType,
            isUpToDate: sandbox.isUpToDate
        };
        
        const filename = `/tmp/execution_${Date.now()}.json`;
        fs.writeFileSync(filename, JSON.stringify(executionInfo, null, 2));
        console.log('💾 Execution info saved to:', filename);
        await sleep(100);
        
        console.log('\\n✅ Script executed successfully!');
        await sleep(100);
        
        // Exit successfully
        process.exit(0);
        
    } catch (error) {
        console.error('❌ Failed to execute in CodeSandbox:', error.message);
        await sleep(100);
        
        if (error.message.includes('unauthorized') || error.message.includes('authentication')) {
            console.error('');
            await sleep(100);
            console.error('🔑 Authentication Error:');
            await sleep(100);
            console.error('1. Check that your CSB_API_KEY is correct');
            await sleep(100);
            console.error('2. Ensure you have a CodeSandbox Pro plan');
            await sleep(100);
            console.error('3. Verify the API key has the necessary permissions');
            await sleep(100);
        } else if (error.message.includes('rate limit')) {
            console.error('');
            await sleep(100);
            console.error('⏱️ Rate Limit Error:');
            await sleep(100);
            console.error('You have exceeded the API rate limit. Please try again later.');
            await sleep(100);
        } else if (error.message.includes('timeout')) {
            console.error('');
            await sleep(100);
            console.error('⏱️ Timeout Error:');
            await sleep(100);
            console.error('The script took too long to execute. Consider optimizing or breaking it down.');
            await sleep(100);
        }
        
        process.exit(1);
    }
}

executeSandbox();
EOF
            
            # Export environment variables for the Node.js script
            export SANDBOX_ID="$sandbox_id"
            export SCRIPT_CONTENT="$script_content"
            
            # Run the Node.js script from the correct directory
            echo "🔧 Running CodeSandbox SDK execution..."
            cd /tmp/codesandbox_project
            node execute_sandbox.js
            """,
            args=[
                Arg(name="sandbox_id", description="Existing sandbox ID to execute script in", required=True),
                Arg(name="script_content", description="Python script content (only used as fallback if main.py doesn't exist)", required=False)
            ]
        )


# Initialize the tools
CodeSandboxSDKTools() 