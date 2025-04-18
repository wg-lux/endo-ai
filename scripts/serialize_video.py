from pathlib import Path
from icecream import ic
import django
import yaml
import os  # Import os

# --- Django Setup ---
# Ensure DJANGO_SETTINGS_MODULE is set correctly
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

from endoreg_db.models import Video
from endoreg_db.serializers.sync.video import VideoSerializer

REPORT_DIR = Path("data/test_reports")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = REPORT_DIR / "video-serializer.yaml"
ic("fetch video")
v = Video.objects.first()
# v.sync_from_raw_video()  # Keep commented unless needed for specific testing
ic(v)
if not v:
    ic("No video found in the database. Exiting.")
    exit()

v_serializer = VideoSerializer(v)
serializer_data = v_serializer.data  # Get the data first
# ic(serializer_data)  # Optional: inspect the data structure

# Explicitly convert to a standard dict to avoid Python-specific tags
plain_dict_data = dict(serializer_data)

ic(f"Writing serialized data to {OUTPUT_PATH}")
with open(file=OUTPUT_PATH, mode="w", encoding="utf-8") as f:
    # write the plain dictionary data to the file using standard dump
    yaml.dump(data=plain_dict_data, stream=f, default_flow_style=False, sort_keys=False)  # Dump the plain dict
    ic(f"Video serializer data written to {OUTPUT_PATH}")
