import os
import random
import string

DB_YAML = "./conf_template/db.yaml"
# Extract the password_file path from the YAML file.
password_file = None
with open(DB_YAML, "r") as f:
    for line in f:
        if line.startswith("password_file:"):
            parts = line.split()
            if len(parts) > 1:
                password_file = parts[1].strip()
            break

if not password_file:
    print("No password_file entry found in", DB_YAML)
    exit(1)

if not os.path.exists(password_file):
    os.makedirs(os.path.dirname(password_file), exist_ok=True)
    # Generate a random password with 16 characters.
    password = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(16)
    )
    with open(password_file, "w", encoding="utf-8") as f:
        f.write(password)
    print(f"Password file created at {password_file}.")
else:
    print(f"Password file already exists at {password_file}.")
