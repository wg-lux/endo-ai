from django.core.management import BaseCommand, call_command
from io import StringIO
from pathlib import Path
from endoreg_db.models import VideoSegmentationLabel, LabelSet, AiModel
from agl_frame_extractor import VideoFrameExtractor
from endo_ai.predictor.model_loader import MultiLabelClassificationNet

from icecream import ic

# Example usage:
# python manage.py import_video ~/test-data/video/lux-gastro-video.mp4
# python manage.py import_video ~/test-data/video/NINJAU_S001_S001_T026.MOV

FPS = 50
SMOOTH_WINDOW_SIZE_S = 1
MIN_SEQ_LEN_S = 0.5
crop_template = [0, 1080, 550, 1920 - 20]  # [top, bottom, left, right]


class Command(BaseCommand):
    help = """
        Imports a .mov file to the database.
        1. Get center by center name from db (default: university_hospital_wuerzburg)
        2. get processor by name (default: olympus_cv_1500)
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--model_name",
            type=str,
            default="multilabel_video_segmentation",
            help="Name of the model to use for segmentation",
        )

        # version: int
        parser.add_argument(
            "--version",
            type=int,
            default=1,
            help="The version of the model",
        )

        # model_path
        parser.add_argument(
            "--model_path",
            type=str,
            default="./data/models/colo_segmentation_RegNetX800MF_6.ckpt",
            help="Path to the model file",
        )

        parser.add_argument(
            "--image_classification_labelset_name",
            type=str,
            default="multilabel_classification_colonoscopy_default",
            help="Name of the LabelSet for image classification",
        )

    def handle(self, *args, **options):
        model_name = options["model_name"]
        version = options["version"]
        model_path = options["model_path"]
        image_classification_labelset_name = options[
            "image_classification_labelset_name"
        ]

        video_segmentation_label_names = options[
            "video_segmentation_label_names"
        ].split(",")

        # Assert labelset exists
        assert LabelSet.objects.filter(
            name=image_classification_labelset_name
        ).exists(), f"LabelSet not found: {image_classification_labelset_name}"

        # Assert vid seg labels
        for label_name in video_segmentation_label_names:
            assert VideoSegmentationLabel.objects.filter(name=label_name).exists(), (
                f"Label not found: {label_name}"
            )

        # assert model exists
        db_ai_model = AiModel.objects.filter(name=model_name).first()
        assert db_ai_model, f"Model not found: {model_name}"

        model_path = Path(model_path).expanduser()

        assert model_path.exists(), f"Model file not found: {model_path}"
