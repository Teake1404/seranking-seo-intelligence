#!/usr/bin/env python3
"""
Setup script for SEranking MCP server integration
Automates the installation and configuration of SEranking MCP
"""
import os
import subprocess
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def setup_seranking_mcp():
    """Setup SEranking MCP server"""
    print("🚀 Setting up SEranking MCP server...")
    
    # Check if git is installed
    success, stdout, stderr = run_command("git --version")
    if not success:
        print("❌ Git is not installed. Please install Git first.")
        return False
    
    # Check if docker is installed
    success, stdout, stderr = run_command("docker --version")
    if not success:
        print("❌ Docker is not installed. Please install Docker first.")
        return False
    
    # Clone the SEranking MCP repository
    mcp_dir = Path("seo-data-api-mcp-server")
    if not mcp_dir.exists():
        print("📥 Cloning SEranking MCP repository...")
        success, stdout, stderr = run_command(
            "git clone https://github.com/seranking/seo-data-api-mcp-server.git"
        )
        if not success:
            print(f"❌ Failed to clone repository: {stderr}")
            return False
        print("✅ Repository cloned successfully")
    else:
        print("📁 MCP repository already exists")
    
    # Build Docker container
    print("🔨 Building Docker container...")
    success, stdout, stderr = run_command("docker compose build", cwd=mcp_dir)
    if not success:
        print(f"❌ Failed to build container: {stderr}")
        return False
    print("✅ Docker container built successfully")
    
    # Create environment file
    env_file = mcp_dir / ".env"
    if not env_file.exists():
        print("📝 Creating environment file...")
        with open(env_file, "w") as f:
            f.write("# SEranking MCP Environment Variables\n")
            f.write("SERANKING_API_TOKEN=your_api_token_here\n")
        print("✅ Environment file created")
        print("⚠️  Please update the SERANKING_API_TOKEN in the .env file")
    
    print("🎉 SEranking MCP setup complete!")
    print("\n📋 Next steps:")
    print("1. Update your API token in seo-data-api-mcp-server/.env")
    print("2. Start the MCP server: cd seo-data-api-mcp-server && docker compose up -d")
    print("3. Test the connection with your SEO Intelligence API")
    
    return True

def create_mcp_config():
    """Create MCP configuration for Claude Desktop"""
    print("\n🔧 Creating Claude Desktop MCP configuration...")
    
    # Get the absolute path to the MCP directory
    mcp_dir = Path("seo-data-api-mcp-server").resolve()
    
    # Claude Desktop config
    claude_config = {
        "mcpServers": {
            "seo-data-api-mcp": {
                "command": "docker",
                "args": [
                    "run",
                    "-i",
                    "--rm",
                    "-e",
                    "SERANKING_API_TOKEN",
                    "se-ranking/seo-data-api-mcp-server"
                ],
                "env": {
                    "SERANKING_API_TOKEN": "your_api_token_here"
                }
            }
        }
    }
    
    # Save config to file
    config_file = Path("claude_desktop_config.json")
    with open(config_file, "w") as f:
        json.dump(claude_config, f, indent=2)
    
    print(f"✅ Claude Desktop config saved to {config_file}")
    print(f"📁 Copy this to: ~/Library/Application Support/Claude/claude_desktop_config.json")
    
    return True

def test_mcp_connection():
    """Test MCP server connection"""
    print("\n🧪 Testing MCP server connection...")
    
    # Check if container is running
    success, stdout, stderr = run_command("docker ps --filter name=seo-data-api-mcp-server")
    if "seo-data-api-mcp-server" in stdout:
        print("✅ MCP server container is running")
        return True
    else:
        print("❌ MCP server container is not running")
        print("💡 Start it with: cd seo-data-api-mcp-server && docker compose up -d")
        return False

if __name__ == "__main__":
    print("🚀 SEranking MCP Setup Script")
    print("=" * 50)
    
    # Setup MCP server
    if setup_seranking_mcp():
        # Create configuration
        create_mcp_config()
        
        # Test connection
        test_mcp_connection()
        
        print("\n🎯 Setup complete! Your SEO Intelligence API can now use SEranking MCP.")
    else:
        print("\n❌ Setup failed. Please check the errors above.")

