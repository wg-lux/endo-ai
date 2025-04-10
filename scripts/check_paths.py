#!/usr/bin/env python
import os
import json
from pathlib import Path

def check_paths():
    """Check and correct path variables in the environment"""
    print("Checking project paths...\n")
    
    # Get current environment state
    env_file = Path(".env")
    env_data = {}
    
    # Load devenv variables
    devenv_vars = {}
    devenv_path = Path(".devenv-vars.json")
    
    if devenv_path.exists():
        try:
            with open(devenv_path, 'r') as f:
                devenv_vars = json.load(f)
        except json.JSONDecodeError:
            print("⚠️  Warning: .devenv-vars.json is not valid JSON")
    else:
        print("⚠️  Warning: .devenv-vars.json file not found")
    
    # Check home directory
    home_dir = devenv_vars.get("HOME_DIR", "") or os.environ.get("HOME", "")
    working_dir = devenv_vars.get("WORKING_DIR", "") or os.path.abspath(os.getcwd())
    
    print(f"HOME_DIR: {home_dir}")
    print(f"WORKING_DIR: {working_dir}")
    
    # Update the devenv vars if needed
    if devenv_path.exists() and (not devenv_vars.get("HOME_DIR") or not devenv_vars.get("WORKING_DIR")):
        devenv_vars["HOME_DIR"] = home_dir
        devenv_vars["WORKING_DIR"] = working_dir
        
        with open(devenv_path, 'w') as f:
            json.dump(devenv_vars, f, indent=2)
        print("\n✅ Updated .devenv-vars.json with correct paths")
    
    # Check if paths in .env match
    if env_file.exists():
        print("\nChecking .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    env_data[key.strip()] = value.strip().strip('"\'')
        
        if env_data.get("DJANGO_HOME_DIR", "") != home_dir:
            print(f"⚠️  Warning: DJANGO_HOME_DIR in .env ({env_data.get('DJANGO_HOME_DIR', '')}) doesn't match expected value ({home_dir})")
        
        if env_data.get("DJANGO_WORKING_DIR", "") != working_dir:
            print(f"⚠️  Warning: DJANGO_WORKING_DIR in .env ({env_data.get('DJANGO_WORKING_DIR', '')}) doesn't match expected value ({working_dir})")
    
if __name__ == "__main__":
    check_paths()
