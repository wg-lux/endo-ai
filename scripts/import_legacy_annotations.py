"""Script to import legacy annotations from the old format to the new format"""

import json
from pathlib import Path

ANNOTATION_FILE = Path("data/import/legacy_annotations/img_dicts.jsonl")
IMAGE_DIR = Path("data/import/legacy_annotations/images")

image_dicts = []

with ANNOTATION_FILE.open("r", encoding="utf-8") as f:
    for line in f:
        image_dicts.append(json.loads(line))
