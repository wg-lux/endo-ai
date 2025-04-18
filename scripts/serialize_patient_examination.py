import json
import yaml  # Ensure you have PyYAML installed
from endoreg_db.models import Video  # adjust import based on your project structure
from endoreg_db.serializers.sync.video import VideoSerializer

import argparse
import sys

# Set up argument parser
parser = argparse.ArgumentParser(description='Serialize a video to JSON and YAML')
parser.add_argument('--video_id', type=int, default=1, help='ID of the video to serialize')
args = parser.parse_args()

# Fetch your Video instance (modify the query as needed)
try:
    video_instance = Video.objects.get(pk=args.video_id)
except Video.DoesNotExist:
    print(f"Error: No video found with ID {args.video_id}")
    sys.exit(1)

# Serialize the Video instance to a Python dict
serializer = VideoSerializer(video_instance)
video_data = serializer.data

# Export to JSON
json_output = json.dumps(video_data, indent=2)
print("JSON Output:")
print(json_output)

# Export to YAML
yaml_output = yaml.safe_dump(video_data)
print("YAML Output:")
print(yaml_output)