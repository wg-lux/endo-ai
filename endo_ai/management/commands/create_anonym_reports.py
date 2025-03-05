from icecream import ic

from django.core.management import BaseCommand  # , call_command
from endoreg_db.models import (
    RawPdfFile,
)


# Example usage:

# python manage.py create_anonym_reports


class Command(BaseCommand):
    """ """

    help = """

    """

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        raw_pdfs = RawPdfFile.objects.all()  # pylint: disable=no-member
        for raw_pdf in raw_pdfs:
            report_file = raw_pdf.get_or_create_report_file()
            ic(report_file)
            ic(f"Text: {report_file.text}")
