# from io import StringIO
# from pathlib import Path
# from icecream import ic

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
    """
    Django management command to predict raw video files using a specified AI model.
    This command processes a raw video file and generates predictions using a specified AI model.
    It supports various options to customize the prediction process, including model selection,
    dataset name, smoothing window size, binarization threshold, and more.
    Attributes:
        help (str): Description of the command.
    Methods:
        add_arguments(parser):
            Adds command-line arguments to the parser.
        handle(*args, **options):
            Executes the command with the provided options.
    """

    help = """
    Django management command to predict raw video files using a specified AI model.
    This command processes a raw video file and generates predictions using a specified AI model.
    It supports various options to customize the prediction process, including model selection,
    dataset name, smoothing window size, binarization threshold, and more.
    Attributes:
        help (str): Description of the command.
    Methods:
        add_arguments(parser):
            Adds command-line arguments to the parser.
        handle(*args, **options):
            Executes the command with the provided options.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--raw_video_uuid", type=str, default=None, help="UUID of the raw video"
        )

    def handle(self, *args, **options):
        video_uuid = options["raw_video_uuid"]

        assert video_uuid is not None, "Raw video UUID must be provided"
        raw_video_object = RawVideoFile.objects.get(uuid=video_uuid)  # pylint: disable=no-member

        assert raw_video_object is not None, "Raw video not found"

        raw_video_object.censor_outside_frames()
        raw_video_object.make_anonymized_video()
