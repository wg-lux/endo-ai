# from io import StringIO
# from pathlib import Path
from icecream import ic

from django.core.management import BaseCommand  # , call_command
from endoreg_db.models import (
    # VideoSegmentationLabel,
    # LabelSet,
    # AiModel,
    ModelMeta,
    RawVideoFile,
)

# from agl_frame_extractor import VideoFrameExtractor
# from endo_ai.predictor.model_loader import MultiLabelClassificationNet


# Example usage:
# python manage.py set_active_meta --model_name image_multilabel_classification_colonoscopy_default


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
        parser.add_argument(
            "--meta_name",
            type=str,
            default="image_multilabel_classification_colonoscopy_default",
            help="Name of the model to use for segmentation",
        )

        parser.add_argument(
            "--model_meta_version",
            type=int,
            default=None,
            help="Model Version",
        )

        parser.add_argument(
            "--dataset_name",
            type=str,
            default="inference_dataset",
            help="Name of the dataset",
        )

        parser.add_argument(
            "--smooth_window_size_s",
            type=float,
            default=1,
            help="Size of the smoothing window in seconds",
        )

        # binarize_threshold
        parser.add_argument(
            "--binarize_threshold",
            type=float,
            default=0.5,
            help="Threshold for binarization",
        )

        # img_suffix
        parser.add_argument(
            "--img_suffix",
            type=str,
            default=".jpg",
            help="Suffix of the image files",
        )

        parser.add_argument(
            "--test_run",
            action="store_true",
            help="Run the command in test mode",
            default=False,
        )

        # n_test_frames = 100
        parser.add_argument(
            "--n_test_frames",
            type=int,
            default=100,
            help="Number of frames to test",
        )

    def handle(self, *args, **options):
        video_uuid = options["raw_video_uuid"]
        dataset_name = options["dataset_name"]
        meta_name = options["meta_name"]
        meta_version = options["model_meta_version"]
        smooth_window_size_s = options["smooth_window_size_s"]
        binarize_threshold = options["binarize_threshold"]
        img_suffix = options["img_suffix"]
        test_run = options["test_run"]
        n_test_frames = options["n_test_frames"]

        if not meta_version:
            version = ModelMeta.get_latest_version(name=meta_name)
            ic(f"No Version Provided, Using Latest Version: {version}")
            assert version is not None, "ModelMeta not found"
        else:
            version = meta_version
            ic("Version Provided: ", version)
            assert version is not None, "ModelMeta not found"

        assert video_uuid is not None, "Raw video UUID must be provided"
        raw_video_object = RawVideoFile.objects.get(uuid=video_uuid)  # pylint: disable=no-member

        assert raw_video_object is not None, "Raw video not found"

        raw_video_object.predict_video(
            model_meta_name=meta_name,
            dataset_name=dataset_name,
            model_meta_version=version,
            smooth_window_size_s=smooth_window_size_s,
            binarize_threshold=binarize_threshold,
            img_suffix=img_suffix,
            test_run=test_run,
            n_test_frames=n_test_frames,
        )
