import os
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "endo_ai.settings_dev")
django.setup()

from endoreg_db.models import Label, RawVideoFile, Video
from icecream import ic

rvf = RawVideoFile.objects.first()
assert rvf is not None

outside_label = Label.objects.get(name="outside")
assert outside_label is not None

outside_segments = rvf.label_video_segments.filter(label=outside_label)

frames = []
for segment in outside_segments:
    ic(segment)
    frames.extend(segment.get_frames())

ic(f"Found {len(frames)} frames in {len(outside_segments)} outside segments")
