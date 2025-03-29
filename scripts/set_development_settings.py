from icecream import ic

env_path = ".env"

with open(env_path, "r", encoding="utf-8") as f:
    env_lines = f.readlines()

# get the value of DJANGO_SETTINGS_MODULE_DEVELOPMENT
for line in env_lines:
    if line.startswith("DJANGO_SETTINGS_MODULE_DEVELOPMENT"):
        SETTINGS_MODULE = line.split("=")[1].strip()
        ic(SETTINGS_MODULE)
        break

assert SETTINGS_MODULE, "DJANGO_SETTINGS_MODULE_PRODUCTION not found in .env file"

# change the value of DJANGO_SETTINGS_MODULE to DJANGO_SETTINGS_MODULE_PRODUCTION
for i, line in enumerate(env_lines):
    if line.startswith("DJANGO_SETTINGS_MODULE"):
        env_lines[i] = f"DJANGO_SETTINGS_MODULE={SETTINGS_MODULE}\n"
        break

with open(env_path, "w", encoding="utf-8") as f:
    f.writelines(env_lines)
