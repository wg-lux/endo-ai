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
import argparse
import sys

# Add command-line argument parsing
parser = argparse.ArgumentParser(description="Serialize a Video model instance to YAML")
parser.add_argument("--video-id", type=int, help="ID of the video to serialize (defaults to first video)")
parser.add_argument("--output", type=str, help="Output file path (defaults to REPORT_DIR/video-serializer.yaml)")
args = parser.parse_args()

# Modify OUTPUT_PATH if specified via command line
if args.output:
    OUTPUT_PATH = Path(args.output)
    # Ensure the directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

ic("fetch video")
try:
    if args.video_id:
        v = Video.objects.get(id=args.video_id)
        ic(f"Fetching video with ID {args.video_id}")
    else:
        v = Video.objects.first()
        ic("Fetching first video (no ID specified)")
except Video.DoesNotExist:
    ic(f"Video not found. {'ID: ' + str(args.video_id) if args.video_id else 'No videos in database.'}")
    sys.exit(1)
except Exception as e:
    ic(f"Error fetching video: {str(e)}")
    sys.exit(1)

# v.sync_from_raw_video()  # Keep commented unless needed for specific testing
ic(v)
if not v:
    ic("No video found in the database. Exiting.")
    sys.exit(1)
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
