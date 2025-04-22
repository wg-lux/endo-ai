from icecream import ic

from django.core.management import BaseCommand  # , call_command
from endoreg_db.models import (
    Video,
)

from endoreg_db.serializers.sync.video import (
    VideoSerializer
)
from endoreg_db.utils import data_paths
import yaml
EXAMINATION_EXPORT_DIR = data_paths["examination_export"]

class Command(BaseCommand):
    """Export anonymized video examination data to YAML files."""

    help = """
    Export all Video objects to individual YAML files using
    ExportPatientExaminationSerializer. Files are named by video UUID
    and written to the configured examination export directory.
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

        # Before exporting, report total count and initialize counters
        total_videos = videos.count()
        self.stdout.write(f"Exporting {total_videos} videos...")
        successful = 0
        failed = 0

        for video in videos:
            try:
                serializer = VideoSerializer(video)
                video_data = serializer.data
                
                export_path = EXAMINATION_EXPORT_DIR / f"{video.uuid}.yaml"
                export_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
                ic(f"Exporting Examination to: {export_path}")

                with open(export_path, "w", encoding="utf-8") as file:
                    # Use default_flow_style=False and explicitly specify Dumper
                    yaml.dump(
                        video_data,
                        file,
                        allow_unicode=True,
                        default_flow_style=False,
                        sort_keys=False,
                        Dumper=yaml.Dumper  # Explicitly use the standard Dumper
                    )

                successful += 1
                # Report progress every 10 videos
                if successful % 10 == 0:
                    self.stdout.write(f"Progress: {successful}/{total_videos}")

            except Exception as e:
                failed += 1
                self.stderr.write(f"Error exporting video {video.uuid}: {e}")

        # Final summary
        self.stdout.write(self.style.SUCCESS(
            f"Export completed. Successfully exported {successful} videos. Failed: {failed}"
        ))
                

