#!/usr/bin/env python3
"""
Setup script for Automated EDA with Dashboard Builder
"""

import subprocess
import sys
import os


def install_requirements():
    """Install Python requirements"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("✅ Python dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Python dependencies: {e}")
        return False
    return True


def install_client_dependencies():
    """Install Node.js dependencies for client"""
    print("Installing Node.js dependencies...")
    client_dir = os.path.join(os.path.dirname(__file__), "..", "client")

    try:
        subprocess.check_call(["npm", "install"], cwd=client_dir)
        print("✅ Node.js dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Node.js dependencies: {e}")
        return False
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js first.")
        return False
    return True


def create_directories():
    """Create necessary directories"""
    print("Creating necessary directories...")
    dirs = ["uploads", "../uploads"]

    for dir_path in dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ Created directory: {dir_path}")
        except Exception as e:
            print(f"❌ Error creating directory {dir_path}: {e}")


def setup_environment():
    """Setup environment variables"""
    print("Setting up environment...")

    env_file = ".env"
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            f.write("# Automated EDA Environment Variables\n")
            f.write("DATABASE_URL=sqlite:///./automated_eda.db\n")
            f.write("SECRET_KEY=your_secret_key_here\n")
        print(f"✅ Created {env_file} - Please update with your API keys")
    else:
        print(f"✅ {env_file} already exists")


def main():
    """Main setup function"""
    print("🚀 Setting up Automated EDA with Dashboard Builder")
    print("=" * 60)

    # Change to server directory
    script_dir = os.path.dirname(__file__)
    if script_dir:
        os.chdir(script_dir)

    # Create directories
    create_directories()

    # Setup environment
    setup_environment()

    # Install Python dependencies
    if not install_requirements():
        print("❌ Setup failed during Python dependency installation")
        return False

    # Install client dependencies
    if not install_client_dependencies():
        print("⚠️  Client dependencies failed, but server can still run")

    print("\n" + "=" * 60)
    print("🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Update the .env file if needed (DATABASE_URL, SECRET_KEY)")
    print("2. Start the server: python main.py")
    print("3. Start the client: cd ../client && npm run dev")
    print("\nFeatures available:")
    print("- ✅ Automated Data Analysis")
    print("- ✅ AI-Powered Insights")
    print("- ✅ Interactive Charts")
    print("- ✅ Automated Dashboard Builder (NEW!)")
    print("- ✅ MCP Integration for Smart Dashboards")
    print("- ✅ Multiple Dashboard Types (Executive, Quality, Exploratory)")
    print("- ✅ Export Capabilities (HTML, JSON)")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
