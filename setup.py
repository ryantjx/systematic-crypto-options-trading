"""
Setup script for the crypto options trading framework.

This script uses uv for fast virtual environment creation and package installation.
Run this script to set up your development environment.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_uv_installed():
    """Check if uv is installed"""
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ uv {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ uv is not installed")
    print("Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh")
    return False

def check_python_version():
    """Check Python version is 3.9+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.9+ required.")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def create_venv():
    """Create virtual environment using uv"""
    base_dir = Path(__file__).parent
    venv_path = base_dir / '.venv'
    
    if venv_path.exists():
        print(f"✓ Virtual environment already exists at {venv_path}")
        return True
    
    print(f"Creating virtual environment at {venv_path}...")
    try:
        result = subprocess.run(
            ['uv', 'venv', str(venv_path)],
            cwd=base_dir,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ Virtual environment created successfully")
            return True
        else:
            print(f"❌ Failed to create virtual environment")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error creating virtual environment: {e}")
        return False

def install_dependencies():
    """Install dependencies using uv pip"""
    base_dir = Path(__file__).parent
    requirements_file = base_dir / 'requirements.txt'
    
    if not requirements_file.exists():
        print(f"❌ requirements.txt not found")
        return False
    
    print(f"\nInstalling dependencies from requirements.txt...")
    try:
        result = subprocess.run(
            ['uv', 'pip', 'install', '-r', str(requirements_file)],
            cwd=base_dir,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_directory_structure():
    """Verify directory structure exists"""
    base_dir = Path(__file__).parent
    required_dirs = [
        'src/data',
        'src/utils',
        'notebooks',
        'tests',
        'data/raw',
        'data/processed',
        'configs',
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ missing")
            all_exist = False
    
    return all_exist

def verify_installation():
    """Verify key packages are installed in the virtual environment"""
    required = ['numpy', 'pandas', 'scipy', 'matplotlib', 'ccxt']
    
    print("\nVerifying installation...")
    all_installed = True
    for package in required:
        try:
            result = subprocess.run(
                ['uv', 'pip', 'show', package],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✓ {package}")
            else:
                print(f"❌ {package} not installed")
                all_installed = False
        except Exception as e:
            print(f"❌ Error checking {package}: {e}")
            all_installed = False
    
    return all_installed

def print_activation_instructions():
    """Print instructions for activating the virtual environment"""
    base_dir = Path(__file__).parent
    venv_path = base_dir / '.venv'
    
    print("\n" + "=" * 60)
    print("To activate the virtual environment, run:")
    print("=" * 60)
    print(f"  source {venv_path}/bin/activate")
    print("\nOr in fish shell:")
    print(f"  source {venv_path}/bin/activate.fish")
    print("\n" + "=" * 60)

def main():
    """Run all setup steps"""
    print("=" * 60)
    print("Crypto Options Trading Framework - Setup")
    print("=" * 60)
    
    print("\n1. Checking uv installation...")
    uv_ok = check_uv_installed()
    if not uv_ok:
        return
    
    print("\n2. Checking Python version...")
    python_ok = check_python_version()
    if not python_ok:
        return
    
    print("\n3. Creating virtual environment...")
    venv_ok = create_venv()
    if not venv_ok:
        return
    
    print("\n4. Installing dependencies...")
    install_ok = install_dependencies()
    if not install_ok:
        return
    
    print("\n5. Checking directory structure...")
    dirs_ok = check_directory_structure()
    
    print("\n6. Verifying installation...")
    verify_ok = verify_installation()
    
    print("\n" + "=" * 60)
    if verify_ok and dirs_ok:
        print("✓ Setup complete! Environment is ready.")
        print("\nNext steps:")
        print("  1. Activate the virtual environment (see below)")
        print("  2. Review notebooks/00_getting_started.ipynb")
        print("  3. Configure API keys in configs/config.py")
        print("  4. Start developing your strategies!")
    else:
        print("⚠ Setup completed with some issues. Check messages above.")
    
    print_activation_instructions()

if __name__ == "__main__":
    main()
