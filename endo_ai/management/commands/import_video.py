from django.core.management import BaseCommand, call_command
from io import StringIO
from pathlib import Path
from endoreg_db.models import RawVideoFile, Center, EndoscopyProcessor
from agl_frame_extractor import VideoFrameExtractor
from endo_ai.predictor.model_loader import MultiLabelClassificationNet

from icecream import ic

# Example usage:
# python manage.py import_video ~/test-data/video/lux-gastro-video.mp4

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
            "--verbose",
            action="store_true",
            help="Display verbose output for all commands",
        )
        parser.add_argument(
            "--center_name",
            type=str,
            default="university_hospital_wuerzburg",
            help="Name of the center to associate with the video",
        )

        parser.add_argument(
            "--processor_name",
            type=str,
            default="olympus_cv_1500",
            help="Name of the processor to associate with the video",
        )

        # add the path to the video file
        parser.add_argument(
            "video_file",
            type=str,
            help="Path to the video file to import",
        )

        # frame dir parent
        parser.add_argument(
            "--frame_dir_root",
            type=str,
            default="~/test_data/db_frame_dir",
            help="Path to the frame directory",
        )

        # video dir
        parser.add_argument(
            "--video_dir_root",
            type=str,
            default="~/test_data/db_video_dir",
            help="Path to the video directory",
        )

        # delete source
        parser.add_argument(
            "--delete_source",
            action="store_true",
            default=False,
            help="Delete the source video file after importing",
        )

        # save video file
        parser.add_argument(
            "--save_video_file",
            action="store_true",
            default=True,
            help="Save the video file to the video directory",
        )

        # model_path
        parser.add_argument(
            "--model_path",
            type=str,
            default="./data/models/colo_segmentation_RegNetX800MF_6.ckpt",
            help="Path to the model file",
        )

    def handle(self, *args, **options):
        verbose = True
        center_name = options["center_name"]
        processor_name = options["processor_name"]
        video_file = options["video_file"]
        frame_dir_root = options["frame_dir_root"]
        video_dir_root = options["video_dir_root"]
        delete_source = options["delete_source"]
        save_video_file = options["save_video_file"]

        assert isinstance(delete_source, bool), "delete_source must be a boolean"

        out = StringIO()

        # Make sure the video file exists
        video_file = Path(video_file).expanduser()
        if not video_file.exists():
            self.stdout.write(self.style.ERROR(f"Video file not found: {video_file}"))
            return

        # Make sure the frame directory exists
        frame_dir_root = Path(frame_dir_root).expanduser()
        frame_dir_root.mkdir(parents=True, exist_ok=True)

        # Make sure the video directory exists
        video_dir_root = Path(video_dir_root).expanduser()
        video_dir_root.mkdir(parents=True, exist_ok=True)

        # Assert Center exists
        try:
            center = Center.objects.get(name=center_name)
            self.stdout.write(self.style.SUCCESS(f"Using center: {center.name_en}"))
        except Center.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Center not found: {center_name}"))
            return

        # Assert Processor Exists
        try:
            processor = EndoscopyProcessor.objects.get(name=processor_name)
            self.stdout.write(self.style.SUCCESS(f"Using processor: {processor.name}"))
        except EndoscopyProcessor.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Processor not found for center: {center_name}")
            )
            return

        # Create the video file object
        video_file_obj = RawVideoFile.create_from_file(
            file_path=video_file,
            center_name=center_name,
            processor_name=processor_name,
            frame_dir_parent=frame_dir_root,
            video_dir=video_dir_root,
            delete_source=delete_source,
            save=save_video_file,
        )

        video_file_obj.extract_frames(quality=2, overwrite=False, ext="jpg")

        video_file_obj.update_text_metadata(ocr_frame_fraction=0.001)

        video_file_obj.generate_anonymized_frames()
