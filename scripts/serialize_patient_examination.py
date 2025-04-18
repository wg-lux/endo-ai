import json
import yaml  # Ensure you have PyYAML installed
from endoreg_db.models import Video  # adjust import based on your project structure
from endoreg_db.serializers.sync. import VideoSerializer

# Fetch your Video instance (modify the query as needed)
video_instance = Video.objects.get(pk=1)

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