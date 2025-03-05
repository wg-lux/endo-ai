from io import StringIO
from pathlib import Path
from django.core.management import BaseCommand
from endoreg_db.models import Patient
from icecream import ic

# Example usage:
# python manage.py create_pseudo_patients


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        patients = Patient.objects.all()

        for i, patient in enumerate(patients):
            ee, rr, vv = patient.export_patient_examinations()
            ic("------")
            ic(i, patient)
            ic("Examinations")
            for e in ee:
                ic(e)
            ic("Reports")
            for r in rr:
                ic(r)

            ic("Videos")
            for v in vv:
                ic(v)
            ic("------")
