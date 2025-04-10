from django.core.management.utils import get_random_secret_key
import subprocess
import os
import json
from pathlib import Path
import shutil

# Load variables from Nix
nix_vars = {}
nix_vars_path = Path("./.devenv-vars.json")
if nix_vars_path.exists():
    with open(nix_vars_path, 'r', encoding="utf-8") as f:
        nix_vars = json.load(f)
    print(f"Loaded Nix variables: {', '.join(nix_vars.keys())}")
else:
    print("No Nix variables file found at .devenv-vars.json")

# use python pathlib to get home and working dir
home_dir = nix_vars.get("HOME_DIR", os.path.expanduser("~"))
working_dir = nix_vars.get("WORKING_DIR", os.path.abspath(os.getcwd()))

nix_vars["HOME_DIR"] = home_dir
nix_vars["WORKING_DIR"] = working_dir

SALT = get_random_secret_key()
SECRET_KEY = get_random_secret_key()

template = Path("./conf_template/default.env")
target = Path("./.env")

# Create a new .env file or use the existing template
if not target.exists():
    shutil.copy(template, target)
    
# Track what we've found or added
found_keys = set()

# Read existing entries
with target.open("r", encoding="utf-8") as f:
    lines = f.readlines()

# Process and update entries
updated_lines = []
for line in lines:
    stripped_line = line.strip()
    if not stripped_line or stripped_line.startswith("#"):
        updated_lines.append(line)
        continue
        
    if "=" not in stripped_line:
        updated_lines.append(line)
        continue
        
    key, value = stripped_line.split("=", 1)
    key = key.strip()
    found_keys.add(key)
    
    # Replace values from nix_vars if present
    if key == "DJANGO_SETTINGS_MODULE" and "DJANGO_MODULE" in nix_vars:
        updated_lines.append(f"{key}={nix_vars['DJANGO_MODULE']}.settings_dev\n")
    elif key == "DJANGO_SETTINGS_MODULE_PRODUCTION" and "DJANGO_MODULE" in nix_vars:
        updated_lines.append(f"{key}={nix_vars['DJANGO_MODULE']}.settings_prod\n")
    elif key == "DJANGO_SETTINGS_MODULE_DEVELOPMENT" and "DJANGO_MODULE" in nix_vars:
        updated_lines.append(f"{key}={nix_vars['DJANGO_MODULE']}.settings_dev\n")
    else:
        updated_lines.append(line)

# Write updated content back
with target.open("w", encoding="utf-8") as f:
    f.writelines(updated_lines)

# Add any missing required entries
with target.open("a", encoding="utf-8") as f:
    if "DJANGO_SECRET_KEY" not in found_keys:
        f.write(f'\nDJANGO_SECRET_KEY="{SECRET_KEY}"')
        
    if "DJANGO_SALT" not in found_keys:
        f.write(f'\nDJANGO_SALT="{SALT}"')
    
    # Add default values for variables that might not be in nix_vars
    default_values = {
        "TEST_RUN": "False",
        "TEST_RUN_FRAME_NUMBER": "1000",
        "RUST_BACKTRACE": "1",
        "DJANGO_DEBUG": "True",
        "DJANGO_FFMPEG_EXTRACT_FRAME_BATCHSIZE": "500"
    }
    
    # Add more variables from nix_vars
    for var_name, prefix in [
        ("HOST", "DJANGO_HOST"),
        ("PORT", "DJANGO_PORT"),
        ("DATA_DIR", "DJANGO_DATA_DIR"),
        ("CONF_DIR", "DJANGO_CONF_DIR"),
        ("HOME_DIR", "HOME_DIR"),
        ("WORKING_DIR", "WORKING_DIR"),
    ]:
        if var_name in nix_vars and prefix not in found_keys:
            f.write(f'\n{prefix}="{nix_vars[var_name]}"')
    
    # Special case for DJANGO_MODULE to add all settings variants
    if "DJANGO_MODULE" in nix_vars:
        module = nix_vars["DJANGO_MODULE"]
        if "DJANGO_SETTINGS_MODULE" not in found_keys:
            f.write(f'\nDJANGO_SETTINGS_MODULE="{module}.settings_dev"')
        if "DJANGO_SETTINGS_MODULE_PRODUCTION" not in found_keys:
            f.write(f'\nDJANGO_SETTINGS_MODULE_PRODUCTION="{module}.settings_prod"')
        if "DJANGO_SETTINGS_MODULE_DEVELOPMENT" not in found_keys:
            f.write(f'\nDJANGO_SETTINGS_MODULE_DEVELOPMENT="{module}.settings_dev"')
    
    # Add default values for missing variables
    for var_name, default_value in default_values.items():
        if var_name not in found_keys:
            f.write(f'\n{var_name}={default_value}')

print(f"Environment file updated at {target}")
