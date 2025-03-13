from django.core.management.utils import get_random_secret_key
import subprocess
import os
from pathlib import Path
import shutil


SALT = get_random_secret_key()
#while "=" in SALT:
#    SALT = get_random_secret_key()

SECRET_KEY=get_random_secret_key()
#while "=" in SECRET_KEY:
    #SECRET_KEY = get_random_secret_key()

template = Path("./conf_template/default.env")
target = Path("./.env")

if not target.exists():
    shutil.copy(template, target)
    
found_salt = False   
found_secret_key = False 
for line in target.open():
    key, value = line.split("=", 1)
    
    if key == "DJANGO_SALT":
        found_salt = True
        
    if key == "DJANGO_SECRET_KEY":
        found_secret_key = True
        
if not found_secret_key:
    with target.open("a") as f:
        f.write(f'\nDJANGO_SECRET_KEY="{SECRET_KEY}"')
        
if not found_salt:
    with target.open("a") as f:
        f.write(f'\nDJANGO_SALT="{SALT}"')
    