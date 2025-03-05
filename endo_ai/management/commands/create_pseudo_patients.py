"""
Management command to import a video file to the database.
"""

from io import StringIO
from pathlib import Path
from django.core.management import BaseCommand
from endoreg_db.models import SensitiveMeta, Patient
from icecream import ic

# Example usage:
# python manage.py create_pseudo_patients


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

    def handle(self, *args, **options):
        verbose = True
        sensitive_metas = SensitiveMeta.objects.all()
        for sensitive_meta in sensitive_metas:
            patient = sensitive_meta.get_or_create_pseudo_patient()

        patients = Patient.objects.all()
        for i, patient in enumerate(patients):
            ic(i, patient)
