import os
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "endo_ai.settings_dev")
django.setup()

dev_out = Path("./data/dev_out.txt")

from endoreg_db.models import LabelRawVideoSegment, RawVideoFile, Video
from icecream import ic

rvf = RawVideoFile.objects.first()
video_meta = rvf.video_meta

ic("First RawVideoFile")
ic(rvf)

ic("The associated Video Meta")
ic(video_meta)

# Initialize_frames
paths = rvf.extract_frames()
rvf.initialize_frames(paths)
