import argparse
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


# Set up argument parser
parser = argparse.ArgumentParser(description='Extract frames from a video')
parser.add_argument('--video_id', type=int, help='ID of the video to extract frames from')
args = parser.parse_args()

# Get video based on arguments or default to first
if args.video_id:
    v = Video.objects.filter(pk=args.video_id).first()
    if v is None:
        print(f"No video found with ID {args.video_id}")
        exit(1)
else:
    v = Video.objects.first()

assert v is not None, "No video found in the database. Please ensure you have a video to work with."
v.extract_frames()
v.set_frames_extracted()

