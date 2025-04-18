from icecream import ic

from django.core.management import BaseCommand  # , call_command
from endoreg_db.models import (
    Video,
)

from endoreg_db.utils import data_paths
import yaml
from endoreg_db.serializers.export_patient_examination import ExportPatientExaminationSerializer

EXAMINATION_EXPORT_DIR = data_paths["examination_export"]



class Command(BaseCommand):
    """ """

    help = """

    """

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        videos = Video.objects.all()

        # Later we can filter by state
        # videos = Video.objects.filter(
        #     state_anonymous_validated=True,
        #     state_dataset_complete=True,
        # )
        for video in videos:
            serializer = ExportPatientExaminationSerializer(video)
            patient_examination_data = serializer.data
            
            export_path = EXAMINATION_EXPORT_DIR / f"{video.uuid}.yaml"
            export_path.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
            ic(f"Exporting Examination to: {export_path}")
            
            with open(export_path, "w", encoding="utf-8") as file:
                # Use default_flow_style=False and explicitly specify Dumper
                yaml.dump(
                    patient_examination_data, 
                    file, 
                    allow_unicode=True, 
                    default_flow_style=False, 
                    sort_keys=False,
                    Dumper=yaml.Dumper  # Explicitly use the standard Dumper
                )

