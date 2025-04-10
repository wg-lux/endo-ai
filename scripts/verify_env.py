import os
import json
from pathlib import Path

def main():
    # Read .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ ERROR: .env file not found")
        return False
    
    env_vars = {}
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip().strip('"').strip("'")
    
    # Read devenv variables
    nix_vars_file = Path(".devenv-vars.json")
    if not nix_vars_file.exists():
        print("❌ WARNING: .devenv-vars.json file not found, can't verify against Nix variables")
        return True
    
    try:
        with open(nix_vars_file, "r", encoding="utf-8") as f:
            nix_vars = json.load(f)
    except json.JSONDecodeError:
        print("❌ ERROR: Invalid .devenv-vars.json file")
        return False
    
    # Verify key environment variables
    checks = []
    
    if "DJANGO_SECRET_KEY" not in env_vars:
        checks.append(("❌ ERROR", "DJANGO_SECRET_KEY missing from .env"))
    
    if "DJANGO_SALT" not in env_vars:
        checks.append(("❌ ERROR", "DJANGO_SALT missing from .env"))
    
    # Check for Nix variable integration
    if "DJANGO_MODULE" in nix_vars:
        expected_settings = f"{nix_vars['DJANGO_MODULE']}.settings_dev"
        if env_vars.get("DJANGO_SETTINGS_MODULE_DEVELOPMENT") != expected_settings:
            checks.append(("⚠️ WARNING", f"DJANGO_SETTINGS_MODULE_DEVELOPMENT is not synchronized with Nix variables"))
    
    # Print verification results
    if checks:
        print("Environment Verification Results:")
        for status, message in checks:
            print(f"  {status}: {message}")
    else:
        print("✅ Environment is correctly configured!")
    
    return len([c for c in checks if c[0] == "❌ ERROR"]) == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
