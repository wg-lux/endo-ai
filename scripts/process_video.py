import os
from pathlib import Path
import dotenv
from endoreg_db.utils.paths import STORAGE_DIR
dotenv.load_dotenv()

import os
from pathlib import Path
import dotenv
from endoreg_db.utils.paths import data_paths
dotenv.load_dotenv()
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Process video and manage database operations.')
parser.add_argument('--rm-db', action='store_true', help='Remove SQLite database')
parser.add_argument('--migrate', action='store_true', help='Run database migrations')
parser.add_argument('--load-base-data', action='store_true', help='Load base data into database')
parser.add_argument('--load-model', action='store_true', help='Load AI model')
parser.add_argument('--import-video', action='store_true', help='Import video file')
parser.add_argument('--video-name', default="NINJAU_S001_S001_T018.mp4", help='Name of video file to import')
parser.add_argument('--all', action='store_true', help='Run all operations')
args = parser.parse_args()

# Set flags based on arguments
RM_DB_SQLITE = args.rm_db or args.all
MIGRATE_DB = args.migrate or args.all
LOAD_BASE_DB_DATA = args.load_base_data or args.all
LOAD_MODEL = args.load_model or args.all
IMPORT_VIDEO = args.import_video or args.all
VIDEO_NAME = args.video_name


# Function to get and strip quotes from env var
def get_env_var(key):
    value = os.getenv(key)
    if value:
        return value.strip('"\'') # Strip both single and double quotes
    return None


print("Loading environment variables from .env file...")
# Validate that the .env file is loaded
# print(f"DJANGO_VIDEO_IMPORT_DATA_DIR: {os.getenv('DJANGO_VIDEO_IMPORT_DATA_DIR')}")

print(f"DJANGO_SETTINGS_MODULE: {get_env_var('DJANGO_SETTINGS_MODULE')}")

from django.core.management import call_command
import django # Import django to call setup()
django.setup()

from endoreg_db.models import AiModel
import subprocess

from endoreg_db.utils.paths import (
    data_paths,
    )

storage_dir = data_paths["storage"]
import_video_dir = data_paths["video_import"]

VIDEO_NAME="NINJAU_S001_S001_T018.mp4"

# ###########
#  reset db.sqlite3
if RM_DB_SQLITE:
    db_file = Path("db.sqlite3")
    if db_file.exists():
        try:
            result = subprocess.run(["rm", str(db_file)], check=True, capture_output=True)
            print(f"Database file removed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to remove database file: {e}")
            print(f"Error output: {e.stderr.decode('utf-8')}")
    else:
        print("Database file does not exist, skipping removal.")

#############################################################
########### RUNNING DJANGO MANAGEMENT COMMANDS ###################
#############################################################
if MIGRATE_DB:
    out = call_command(
        "migrate",
    )
    print(out)

if LOAD_BASE_DB_DATA:
    out = call_command(
        "load_base_db_data"
    )
    print(out)


if LOAD_MODEL:
    # run django management commands
    print("Calling create_multilabel_model_meta command...")
    model_path_str = "~/test-data/model/colo_segmentation_RegNetX800MF_6.ckpt"
    expanded_model_path = Path(model_path_str).expanduser().resolve()
    print(f"Expanded Model Path: {expanded_model_path}")

    # Ensure the model path exists before calling the command if necessary
    # assert expanded_model_path.exists(), f"Model path {expanded_model_path} does not exist"

    # Check if a model exists:
    try:
        model = AiModel.objects.get(name="image_multilabel_classification_colonoscopy_default")
        print(f"Model found: {model}")
    except AiModel.DoesNotExist:
        print(f"Model not found in the database. Proceeding to create a new one.")
        out = call_command(
            "create_multilabel_model_meta",
            model_path=str(expanded_model_path), # Pass the expanded path as string
        )
        print(out)

if IMPORT_VIDEO:
    # import Video:
    # python manage.py import_video ~/test-data/video/lux-gastro-video.mp4
    print("Calling import_video command...")
    out = call_command(
        "import_video",
        str(import_video_dir / VIDEO_NAME) 
    )

# # # Predict Video:
# # # python manage.py predict_raw_video_files
# # #FIXME: This command should get all video files without initial prediction and run it

# # print("Calling predict_raw_video_files command...")
# # out = call_command(
# #     "predict_raw_video_files",
# #     str(video_path), # Pass the absolute path as string
# # )
# # print(out)
# # # Create Pseudo Examination:
# # # python manage.py create_pseudo_examinations # Use Sensitive Meta to create Patient Examination
# # print("Calling create_pseudo_examinations command...")
# # out = call_command(
# #     "create_pseudo_examinations",
# #     # str(video_path), # Pass the absolute path as string
# # )
# # print(out)

