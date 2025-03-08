# from io import StringIO
# from pathlib import Path
from icecream import ic

from django.core.management import BaseCommand  # , call_command
from endoreg_db.models import (
    # VideoSegmentationLabel,
    # LabelSet,
    # AiModel,
    # ModelMeta,
    RawVideoFile,
)

# from agl_frame_extractor import VideoFrameExtractor
# from endo_ai.predictor.model_loader import MultiLabelClassificationNet


# Example usage:

# python manage.py censor_outside --raw_video_uuid 138c846e649a40eb84d6633c99f7e704


class Command(BaseCommand):
    """ """

    help = """

    """

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        raw_video_files = RawVideoFile.objects.all()  # pylint: disable=no-member

        for raw_video in raw_video_files:
            raw_video.censor_outside_frames()
            video = raw_video.get_or_create_video()
            ic(video)
            video.sync_from_raw_video()
