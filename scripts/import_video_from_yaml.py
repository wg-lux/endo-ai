import os
import django
from pathlib import Path
import yaml
from icecream import ic
from datetime import datetime

# --- Django Setup ---
# Ensure DJANGO_SETTINGS_MODULE is set correctly
# If running this script directly, you might need to adjust the path
# or ensure your environment variables are set.
try:
    settings_module = os.environ['DJANGO_SETTINGS_MODULE']
except KeyError:
    # Default to dev settings if not set, adjust if necessary
    settings_module = "endo_ai.settings_dev"
    print(f"Warning: DJANGO_SETTINGS_MODULE not set, defaulting to {settings_module}")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

print(f"Using Django settings: {settings_module}")
django.setup()
# --- End Django Setup ---

from django.db import transaction
from endoreg_db.models import (
    Video,
    Patient,
    Center,
    Label,
    LabelVideoSegment,
    Gender,
    SensitiveMeta,
    VideoMeta,
    EndoscopyProcessor,
    Endoscope
)

# --- Configuration ---
YAML_INPUT_PATH = Path("data/test_reports/video-serializer.yaml")

# --- Main Import Logic ---
def import_video_from_yaml(file_path: Path):
    """
    Reads video data from a YAML file and creates corresponding objects in the database.
    """
    if not file_path.exists():
        ic(f"Error: YAML file not found at {file_path}")
        return

    ic(f"Loading data from: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = yaml.safe_load(f)
            if isinstance(data, dict) and 'patient' in data and 'file' in data:
                video_data = data
            else:
                ic("Warning: Unexpected YAML structure. Assuming top-level dict is video data.")
                video_data = data
        except yaml.YAMLError as e:
            ic(f"Error parsing YAML file: {e}")
            return
        except Exception as e:
            ic(f"An unexpected error occurred during YAML loading: {e}")
            return

    if not video_data:
        ic("Error: No data loaded from YAML.")
        return

    ic("YAML data loaded successfully.")

    try:
        with transaction.atomic():
            # 1. Process Center
            center_data = video_data.get('patient', {}).get('center', {})
            center_name = center_data.get('name')
            if not center_name:
                raise ValueError("Center name is missing in YAML data.")
            try:
                center_instance = Center.objects.get(name=center_name)
                ic(f"Found existing Center: {center_instance.name}")
            except Center.DoesNotExist:
                raise ValueError(f"Center '{center_name}' not found in the database. Please ensure it exists.")

            # 2. Process Patient
            patient_data = video_data.get('patient', {})
            first_name = patient_data.get('first_name')
            last_name = patient_data.get('last_name')
            dob_str = patient_data.get('dob')
            gender_name = patient_data.get('gender')

            if not all([first_name, last_name, dob_str]):
                raise ValueError("Patient first name, last name, or DOB is missing in YAML data.")

            try:
                dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError(f"Invalid date format for DOB: '{dob_str}'. Expected YYYY-MM-DD.")

            gender_instance = None
            if gender_name:
                try:
                    gender_instance = Gender.objects.get(name=gender_name)
                    ic(f"Found Gender: {gender_instance.name}")
                except Gender.DoesNotExist:
                    ic(f"Warning: Gender '{gender_name}' not found. Skipping gender assignment.")

            patient_defaults = {
                'gender': gender_instance,
            }
            patient_instance, created = Patient.objects.get_or_create(
                center=center_instance,
                first_name=first_name,
                last_name=last_name,
                dob=dob_date,
                defaults=patient_defaults
            )
            if created:
                ic(f"Created new Patient: {patient_instance}")
            else:
                ic(f"Found existing Patient: {patient_instance}")

            # 3. Process SensitiveMeta
            sensitive_meta_data = video_data.get('sensitive_meta')
            sensitive_meta_instance = None
            if sensitive_meta_data:
                ic("SensitiveMeta data found in YAML - import logic not yet implemented.")
            else:
                ic("No SensitiveMeta data found in YAML.")

            # 4. Process VideoMeta
            video_meta_data = video_data.get('video_meta')
            video_meta_instance = None
            processor_instance = None
            endoscope_instance = None
            if video_meta_data:
                ic("Processing VideoMeta data...")
                processor_data = video_meta_data.get('processor', {})
                processor_name = processor_data.get('name')
                if not processor_name:
                    raise ValueError("EndoscopyProcessor name is missing in video_meta data.")
                processor_instance, proc_created = EndoscopyProcessor.objects.get_or_create(
                    name=processor_name,
                )
                if proc_created:
                    ic(f"Created EndoscopyProcessor: {processor_instance.name}")
                else:
                    ic(f"Found existing EndoscopyProcessor: {processor_instance.name}")

                endoscope_data = video_meta_data.get('endoscope')
                if isinstance(endoscope_data, dict):
                    endoscope_name = endoscope_data.get('name')
                    if not endoscope_name:
                        raise ValueError("Endoscope name is missing in video_meta data.")
                    endoscope_instance, endo_created = Endoscope.objects.get_or_create(
                        name=endoscope_name,
                    )
                elif isinstance(endoscope_data, int):
                    try:
                        endoscope_instance = Endoscope.objects.get(pk=endoscope_data)
                        ic(f"Found existing Endoscope by ID: {endoscope_instance.pk}")
                    except Endoscope.DoesNotExist:
                        raise ValueError(f"Endoscope with ID {endoscope_data} not found.")
                elif endoscope_data is None:
                    ic("Warning: Endoscope data is missing in video_meta. Skipping endoscope assignment.")
                else:
                    raise ValueError(f"Unexpected format for endoscope data: {endoscope_data}")

                if processor_instance:
                    vm_defaults = {}
                    video_meta_instance, vm_created = VideoMeta.objects.get_or_create(
                        center=center_instance,
                        processor=processor_instance,
                        endoscope=endoscope_instance,
                        defaults=vm_defaults
                    )
                    if vm_created:
                        ic(f"Created VideoMeta for Center '{center_instance.name}' linking Processor '{processor_instance.name}' and Endoscope '{getattr(endoscope_instance, 'name', None)}'")
                    else:
                        ic(f"Found existing VideoMeta for Center '{center_instance.name}' linking Processor '{processor_instance.name}' and Endoscope '{getattr(endoscope_instance, 'name', None)}'")
                else:
                    ic("Error: Cannot create VideoMeta without an EndoscopyProcessor.")
                    raise ValueError("Cannot create VideoMeta without an EndoscopyProcessor.")
            else:
                ic("Warning: No video_meta data found in YAML.")
                raise ValueError("video_meta data is missing in YAML, which is required by Video.save()")

            # 5. Create or Update Video
            video_file_path = video_data.get('file')
            video_uuid = video_data.get('uuid')
            assert video_uuid, "UUID is required for Video object creation."
            if not video_file_path:
                raise ValueError("Video file path is missing in YAML data.")

            if os.path.isabs(video_file_path):
                ic(f"Warning: Video file path '{video_file_path}' appears absolute. Expected relative path. Attempting import anyway.")

            existing_video = Video.objects.filter(uuid=video_uuid).first()
            if existing_video:
                ic(f"Video with relative file path '{video_file_path}' for patient {patient_instance} already exists (ID: {existing_video.id}). Checking for updates.")
                video_instance = existing_video
                if video_meta_instance and existing_video.video_meta != video_meta_instance:
                    ic(f"Updating existing video's VideoMeta and Processor.")
                    existing_video.video_meta = video_meta_instance
                    existing_video.processor = processor_instance
                    existing_video.save(update_fields=['video_meta', 'processor'])
                elif not video_meta_instance:
                    ic("Warning: YAML has no video_meta data, but existing video might. No update performed on meta.")
            else:
                ic(f"Creating new Video object with relative file path: {video_file_path}")
                video_instance = Video.objects.create(
                    uuid = video_uuid,
                    patient=patient_instance,
                    sensitive_meta=sensitive_meta_instance,
                    video_meta=video_meta_instance,
                    processor=processor_instance,
                    file=video_file_path,
                    center=patient_instance.center
                )
                ic(f"Created Video with ID: {video_instance.id}")

            # 6. Process LabelVideoSegments
            segments_data = video_data.get('label_video_segments', [])
            ic(f"Processing {len(segments_data)} label video segments...")
            for segment_data in segments_data:
                label_name = segment_data.get('label', {}).get('name')
                start_frame = segment_data.get('start_frame_number')
                end_frame = segment_data.get('end_frame_number')
                source = segment_data.get('source')

                if not label_name or start_frame is None or end_frame is None:
                    ic(f"Warning: Skipping segment due to missing data: {segment_data}")
                    continue

                try:
                    label_instance = Label.objects.get(name=label_name)
                except Label.DoesNotExist:
                    ic(f"Warning: Label '{label_name}' not found. Skipping segment for this label.")
                    continue

                segment_instance, segment_created = LabelVideoSegment.objects.update_or_create(
                    video=video_instance,
                    label=label_instance,
                    start_frame_number=start_frame,
                    end_frame_number=end_frame,
                    defaults={'source': source}
                )
                if segment_created:
                    ic(f"Created LabelVideoSegment: {label_instance.name} ({start_frame}-{end_frame})")
            ic("Import process completed successfully within transaction.")

    except (Center.DoesNotExist, Label.DoesNotExist, ValueError, Patient.DoesNotExist, Gender.DoesNotExist, EndoscopyProcessor.DoesNotExist, Endoscope.DoesNotExist) as e:
        ic(f"Error during import: {e}")
        ic("Transaction rolled back.")
    except Exception as e:
        ic(f"An unexpected error occurred during database operations: {e}")
        ic("Transaction rolled back.")

# --- Script Execution ---
if __name__ == "__main__":
    ic("Starting video import script...")
    import_video_from_yaml(YAML_INPUT_PATH)
    ic("Script finished.")
