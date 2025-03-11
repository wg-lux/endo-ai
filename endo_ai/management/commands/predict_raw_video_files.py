from icecream import ic

from django.core.management import BaseCommand  # , call_command
from endoreg_db.models import (
    ModelMeta,
    RawVideoFile,
)


# Example usage:
# python manage.py predict_raw_video_file --raw_video_uuid 138c846e649a40eb84d6633c99f7e704 --model_meta_version 7 --test_run


class Command(BaseCommand):
    help = """
    """

    def add_arguments(self, parser):
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

        raw_video_files = RawVideoFile.objects.all()

        for raw_video_file in raw_video_files:
            raw_video_file.predict_video(
                model_meta_name=meta_name,
                dataset_name=dataset_name,
                model_meta_version=version,
                smooth_window_size_s=smooth_window_size_s,
                binarize_threshold=binarize_threshold,
                img_suffix=img_suffix,
                test_run=test_run,
                n_test_frames=n_test_frames,
            )
