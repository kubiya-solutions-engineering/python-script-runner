from typing import List, Optional, Dict, Any
from kubiya_sdk.tools import Tool, Arg, FileSpec
from .common import COMMON_FILES, COMMON_ENV

CODESANDBOX_ICON_URL = "https://codesandbox.io/favicon.ico"

DEFAULT_CODESANDBOX_MERMAID = """
```mermaid
classDiagram
    class Tool {
        <<interface>>
        +get_args()
        +get_content()
        +get_image()
    }
    class CodeSandboxTool {
        -content: str
        -args: List[Arg]
        -image: str
        +__init__(name, description, content, args, image)
        +get_args()
        +get_content()
        +get_image()
        +get_file_specs()
        +validate_args(args)
        +get_error_message(args)
        +get_environment()
    }
    Tool <|-- CodeSandboxTool
```
"""

class CodeSandboxTool(Tool):
    """Base class for all CodeSandbox tools using the new SDK."""
    
    name: str
    description: str
    content: str = ""
    args: List[Arg] = []
    image: str = "node:18-alpine"
    icon_url: str = CODESANDBOX_ICON_URL
    type: str = "docker"
    mermaid: str = DEFAULT_CODESANDBOX_MERMAID
    
    def __init__(self, name, description, content, args=None, image="node:18-alpine"):
        # Add SDK installation and setup to the beginning of content
        enhanced_content = f"""
        #!/bin/bash
        set -e
        
        # Create working directory for Node.js project
        mkdir -p /tmp/codesandbox_project
        cd /tmp/codesandbox_project
        
        # Initialize npm project if package.json doesn't exist
        if [ ! -f package.json ]; then
            echo "📦 Initializing npm project..."
            npm init -y >/dev/null 2>&1
        fi
        
        # Install CodeSandbox SDK locally
        echo "📦 Installing CodeSandbox SDK..."
        npm install @codesandbox/sdk >/dev/null 2>&1 || {{
            echo "❌ Failed to install CodeSandbox SDK"
            exit 1
        }}
        echo "✅ CodeSandbox SDK installed successfully"
        
        # Validate API key
        if [ -z "$CSB_API_KEY" ]; then
            echo "❌ CSB_API_KEY environment variable is not set"
            echo ""
            echo "To configure the CodeSandbox API key:"
            echo "1. Go to https://codesandbox.io/dashboard/settings"
            echo "2. Navigate to 'API Keys' or 'Personal Access Tokens'"
            echo "3. Create a new API key"
            echo "4. Set the CSB_API_KEY environment variable"
            echo ""
            echo "Note: You need a CodeSandbox Pro plan to access the API"
            exit 1
        fi
        
        {content}
        """
        
        super().__init__(
            name=name,
            description=description,
            content=enhanced_content,
            args=args or [],
            image=image,
            icon_url=CODESANDBOX_ICON_URL,
            type="docker",
            with_files=COMMON_FILES,
            env=COMMON_ENV,
            secrets=["CSB_API_KEY"]  # Using the new SDK environment variable name
        )

    def get_args(self) -> List[Arg]:
        """Return the tool's arguments."""
        return self.args

    def get_content(self) -> str:
        """Return the tool's shell script content."""
        return self.content

    def get_image(self) -> str:
        """Return the Docker image to use."""
        return self.image

    def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validate the provided arguments."""
        required_args = [arg.name for arg in self.args if arg.required]
        return all(arg in args and args[arg] for arg in required_args)

    def get_error_message(self, args: Dict[str, Any]) -> Optional[str]:
        """Return error message if arguments are invalid."""
        missing_args = []
        for arg in self.args:
            if arg.required and (arg.name not in args or not args[arg.name]):
                missing_args.append(arg.name)
        
        if missing_args:
            return f"Missing required arguments: {', '.join(missing_args)}"
        return None 