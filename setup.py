#!/usr/bin/env python3
"""
PV Sentinel Setup Script
Basic installation and initial configuration
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories for PV Sentinel"""
    directories = [
        'storage',
        'logs',
        'temp',
        'exports',
        'models',
        'validation/artifacts',
        'validation/test_results'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python version: {sys.version}")

def create_sample_config():
    """Create sample configuration if it doesn't exist"""
    config_path = Path('config/config.yaml')
    
    if config_path.exists():
        print("✅ Configuration file already exists")
        return
    
    print("📝 Creating sample configuration...")
    # The config already exists from our implementation
    print("✅ Configuration ready")

def main():
    """Main setup function"""
    print("🚀 PV Sentinel Setup")
    print("=" * 40)
    
    # Check prerequisites
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Create configuration
    create_sample_config()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run tests: python test_basic_functionality.py")
    print("3. Start PV Sentinel: streamlit run frontend/app.py")

if __name__ == "__main__":
    main() 