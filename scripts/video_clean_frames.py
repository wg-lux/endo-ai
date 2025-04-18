import os
import django
# --- Django Setup ---
# Ensure DJANGO_SETTINGS_MODULE is set correctly
# If running this script directly, you might need to adjust the path
# or ensure your environment variables are set.
try:
    settings_module = os.environ['DJANGO_SETTINGS_MODULE']
except KeyError:
    # Default to dev settings if not set, adjust if necessary
    settings_module = "endo_ai.settings_dev"
    print(f"Warning: DJANGO_SETTINGS_MODULE not set, defaulting to {settings_module}")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

print(f"Using Django settings: {settings_module}")
django.setup()
# --- End Django Setup ---

from endoreg_db.models import (
    Video
)

v = Video.objects.first()

assert v is not None, "No video found in the database. Please ensure you have a video to work with."

v.delete_frames()
