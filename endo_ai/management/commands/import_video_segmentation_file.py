"""
Management command to import a video file to the database.
"""

from io import StringIO
from pathlib import Path
from django.core.management import BaseCommand
from endoreg_db.models import (
    RawVideoFile,
    Center,
    EndoscopyProcessor,
)


class Command(BaseCommand):
    """Management Command to import a video file to the database"""

    help = """
        Imports a .mov file to the database.
        1. Get center by center name from db (default: university_hospital_wuerzburg)
        2. get processor by name (default: olympus_cv_1500)
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--video_uuid",
            type=str,
            help="UUID of the video to import",
        )

        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Display verbose output for all commands",
        )

    def handle(self, *args, **options):
        verbose = True
        video_uuid = options["video_uuid"]

        raw_video = RawVideoFile.objects.get(uuid=video_uuid)

        assert raw_video is not None, f"Video with UUID {video_uuid} not found"

        ic(raw_video)
