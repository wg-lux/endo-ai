from django.core.management import BaseCommand, call_command
from io import StringIO
from pathlib import Path
from endoreg_db.models import VideoSegmentationLabel, LabelSet, AiModel, ModelMeta
from agl_frame_extractor import VideoFrameExtractor
from endo_ai.predictor.model_loader import MultiLabelClassificationNet

from icecream import ic

# Example usage:
# python manage.py set_active_meta --model_name image_multilabel_classification_colonoscopy_default


class Command(BaseCommand):
    """
    A Django management command to set the active metadata for a specified AI model.
    This command allows you to specify the model name and the metadata version \
        to set the active metadata for the model.
    If the metadata version is not provided, it will use the latest version available.
    Arguments:
        --model_name (str): Name of the model to use for segmentation. \
            Default is "image_multilabel_classification_colonoscopy_default".
        --model_meta_version (int): Version of the model metadata. Default is None.
    Usage:
        python manage.py set_active_meta --model_name <model_name> \
            --model_meta_version <model_meta_version>
    """

    help = """A Django management command to set the active metadata for a specified AI model.
    This command allows you to specify the model name and the metadata version to set the active metadata for the model. 
    If the metadata version is not provided, it will use the latest version available.
    Arguments:
        --model_name (str): Name of the model to use for segmentation. Default is "image_multilabel_classification_colonoscopy_default".
        --model_meta_version (int): Version of the model metadata. Default is None.
    Usage:
        python manage.py set_active_meta --model_name <model_name> --model_meta_version <model_meta_version>
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--model_name",
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

    def handle(self, *args, **options):
        model_name = options["model_name"]
        meta_name = options["model_name"]
        meta_version = options["model_meta_version"]

        model = AiModel.objects.get(name=model_name)

        if not meta_version:
            version = ModelMeta.get_latest_version(name=meta_name)
            assert version is not None, "ModelMeta not found"

        meta_version = version

        AiModel.set_active_model_meta(model_name, meta_name, meta_version)
