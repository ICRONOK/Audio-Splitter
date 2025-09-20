#!/usr/bin/env python3
"""Verification script for minimal distribution"""

import sys
from pathlib import Path

def verify():
    """Verify minimal distribution"""
    print("🔍 Verifying Audio Splitter CLI - Minimal Distribution")
    print("=" * 55)
    
    # Check files
    required_files = [
        "main.py", "requirements.txt", "setup.py", "README.md",
        "audio_splitter/__init__.py",
        "audio_splitter/core/splitter.py",
        "audio_splitter/ui/cli.py"
    ]
    
    missing = [f for f in required_files if not Path(f).exists()]
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    
    print(f"✅ All {len(required_files)} key files present")
    
    # Test imports
    try:
        from audio_splitter.core.splitter import AudioSplitter
        from audio_splitter.ui.cli import main_cli
        print("✅ Core imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    print("\n🎉 Minimal distribution verified successfully!")
    print("\n📋 Usage:")
    print("  pip install -r requirements.txt")
    print("  python main.py --help")
    print("  python main.py")
    
    return True

if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)
