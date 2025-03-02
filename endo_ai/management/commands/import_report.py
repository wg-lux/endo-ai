"""
Management command to import a video file to the database.
"""

from io import StringIO
from pathlib import Path
from django.core.management import BaseCommand
from endoreg_db.models import (
    RawPdfFile,
    PdfType,
    Center,
    EndoscopyProcessor,
)
from icecream import ic

# Example usage:
# python manage.py import_report ~/test-data/report/lux-gastro-report.pdf

FPS = 50
SMOOTH_WINDOW_SIZE_S = 1
MIN_SEQ_LEN_S = 0.5
crop_template = [0, 1080, 550, 1920 - 20]  # [top, bottom, left, right]


class Command(BaseCommand):
    """Management Command to import a video file to the database"""

    help = """
        Imports a .pdf file to the database.
        1. Get center by center name from db (default: university_hospital_wuerzburg)
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Display verbose output for all commands",
        )

        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the Report file to import",
        )
        parser.add_argument(
            "--center_name",
            type=str,
            default="university_hospital_wuerzburg",
            help="Name of the center to associate with the video",
        )

        # delete source
        parser.add_argument(
            "--delete_source",
            action="store_true",
            default=False,
            help="Delete the source video file after importing",
        )

        parser.add_argument(
            "--save",
            action="store_true",
            default=False,
            help="Save the report object to the database",
        )

    def handle(self, *args, **options):
        verbose = True
        center_name = options["center_name"]
        file_path = options["file_path"]
        delete_source = options["delete_source"]
        save = options["save"]

        assert isinstance(delete_source, bool), "delete_source must be a boolean"

        out = StringIO()

        # Make sure the Report file exists
        file_path = Path(file_path).expanduser()
        if not file_path.exists():
            self.stdout.write(self.style.ERROR(f"Report file not found: {file_path}"))  # pylint: disable=no-member
            return

        # # Make sure the Pdf directory exists
        # report_dir_root = Path(report_dir_root).expanduser()
        # report_dir_root.mkdir(parents=True, exist_ok=True)

        # Create the video file object
        report_file_obj = RawPdfFile.create_from_file(
            file_path=file_path,
            center_name=center_name,
            delete_source=delete_source,
            save=save,
        )

        # TODO Implement assigning pdfType to the report file object
        if "report" in file_path.name:
            pdf_type_name = "ukw-endoscopy-examination-report-generic"
        elif "histo" in file_path.name:
            pdf_type_name = "ukw-endoscopy-histology-report-generic"  # Not yet working

        pdf_type = PdfType.objects.get(name=pdf_type_name)
        report_file_obj.pdf_type = pdf_type
        report_file_obj.process_file(verbose=verbose)

        ic(report_file_obj.sensitive_meta)
