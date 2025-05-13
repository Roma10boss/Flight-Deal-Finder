#!/usr/bin/env python3
"""
Quick Airport Data Setup Script
One-click solution to extract and integrate airport data
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = ['requests', 'beautifulsoup4', 'lxml']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        return False
    return True

def install_dependencies():
    """Install required packages"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    print("Dependencies installed successfully!")

def run_extraction():
    """Run the airport extraction script"""
    print("\n" + "="*50)
    print("STEP 1: Extracting Airport Data")
    print("="*50)
    
    if not os.path.exists('airport_extractor.py'):
        print("ERROR: airport_extractor.py not found!")
        return False
    
    result = subprocess.run([sys.executable, 'airport_extractor.py'])
    
    if result.returncode != 0:
        print("ERROR: Extraction failed!")
        return False
    
    print("Extraction completed successfully!")
    return True

def run_integration():
    """Run the integration script"""
    print("\n" + "="*50)
    print("STEP 2: Integrating Airport Data")
    print("="*50)
    
    if not os.path.exists('integrate_airports.py'):
        print("ERROR: integrate_airports.py not found!")
        return False
    
    result = subprocess.run([sys.executable, 'integrate_airports.py'])
    
    if result.returncode != 0:
        print("ERROR: Integration failed!")
        return False
    
    print("Integration completed successfully!")
    return True

def backup_files():
    """Backup existing files before modification"""
    print("\n" + "="*50)
    print("Creating Backups")
    print("="*50)
    
    files_to_backup = [
        'public/index.html',
        'server.js'
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            backup_name = f"{file}.backup.{int(time.time())}"
            try:
                with open(file, 'r', encoding='utf-8') as src:
                    with open(backup_name, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                print(f"Backed up {file} to {backup_name}")
            except Exception as e:
                print(f"Warning: Could not backup {file}: {e}")

def main():
    print("="*50)
    print("Flight Deals Airport Data Setup")
    print("="*50)
    
    # Check Python version
    if sys.version_info < (3, 6):
        print("ERROR: Python 3.6 or higher is required!")
        sys.exit(1)
    
    # Check for required files
    required_files = ['airport_extractor.py', 'integrate_airports.py', 'requirements.txt']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"ERROR: Missing required files: {', '.join(missing_files)}")
        print("Please ensure all script files are in the current directory.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\nInstalling missing dependencies...")
        try:
            install_dependencies()
        except Exception as e:
            print(f"ERROR: Failed to install dependencies: {e}")
            print("\nPlease install manually using: pip install -r requirements.txt")
            sys.exit(1)
    
    # Create backup
    backup_files()
    
    # Run extraction
    if not run_extraction():
        print("\nERROR: Airport extraction failed!")
        print("Please check the error messages above.")
        sys.exit(1)
    
    # Check if extraction created the necessary files
    if not os.path.exists('airports.json'):
        print("\nERROR: airports.json was not created!")
        print("The extraction process may have failed.")
        sys.exit(1)
    
    # Run integration
    if not run_integration():
        print("\nERROR: Integration failed!")
        print("Please check the error messages above.")
        sys.exit(1)
    
    # Final summary
    print("\n" + "="*50)
    print("SETUP COMPLETE!")
    print("="*50)
    
    if os.path.exists('airports.json'):
        import json
        with open('airports.json', 'r', encoding='utf-8') as f:
            airports = json.load(f)
        
        countries = set(airport['country'] for airport in airports)
        
        print(f"\nSuccess! Your flight deals website now has:")
        print(f"✓ {len(airports)} international airports")
        print(f"✓ {len(countries)} countries")
        print(f"✓ Full autocomplete functionality")
        print(f"✓ Updated server and client files")
        
        print("\nSample airports added:")
        for airport in airports[:5]:
            print(f"  {airport['code']} - {airport['name']} ({airport['city']}, {airport['country']})")
        
        print("\nNext steps:")
        print("1. Start your server: npm start")
        print("2. Test the autocomplete functionality")
        print("3. Try searching for flights")
        print("4. Check the settings page")
        
        print("\nBackup files created - you can restore them if needed.")
    else:
        print("\nWarning: Could not verify the setup. Please check manually.")

if __name__ == "__main__":
    main()