from pathlib import Path
from icecream import ic
import django
import yaml

DJANGO_SETTINGS_MODULE = "endo_ai.settings_dev"
django.setup()

from endoreg_db.models import Video
from endoreg_db.serializers.sync.video import VideoSerializer



REPORT_DIR = Path("data/test_reports")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = REPORT_DIR / "video-serializer.yaml"
ic("fetch video")
v = Video.objects.first()
ic(v)
v_serializer = VideoSerializer(v)
# ic(v_serializer.data)

# configure yaml dumper
yaml.Dumper.ignore_aliases = lambda self, data: True
with open(file=OUTPUT_PATH, mode="w", encoding = "utf-8") as f:
    # write the video serializer data to the file
    yaml.dump(v_serializer.data, f, default_flow_style=False)
    ic(f"Video serializer data written to {OUTPUT_PATH}")
