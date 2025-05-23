import os
from pathlib import Path
import dotenv
dotenv.load_dotenv()
import argparse
import subprocess
import django
from django.core.management import call_command
from endoreg_db.utils.paths import data_paths

# Short Test Video: NINJAU_S001_S001_T023.mp4

# --- Example Usage ---
# Full Pipeline (Long Video)
# # python scripts/process_video.py --rm-db --migrate --load-base-data --load-model --import-video --video-name NINJAU_S001_S001_T018.mp4
# # python scripts/process_video.py --all --video-name NINJAU_S001_S001_T018.mp4

# Full Pipeline (Short Video)
# # python scripts/process_video.py --rm-db --migrate --load-base-data --load-model --import-video --video-name NINJAU_S001_S001_T023.mp4

# python scripts/process_video.py --all --video-name NINJAU_S001_S001_T023.mp4

# Predict Videos
# # python scripts/process_video.py --predict

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description='Process video and manage database operations.')
parser.add_argument('--rm-db', action='store_true', help='Remove SQLite database')
parser.add_argument('--migrate', action='store_true', help='Run database migrations')
parser.add_argument('--load-base-data', action='store_true', help='Load base data into database')
parser.add_argument('--load-model', action='store_true', help='Load AI model')
parser.add_argument('--import-video', action='store_true', help='Import video file')
parser.add_argument('--predict', action='store_true', help='Predict video using AI model')
parser.add_argument('--video-name', default="NINJAU_S001_S001_T023.mp4", help='Name of video file to import')
parser.add_argument('--create-pseudo-examinations', action='store_true', help='Create pseudo examination')
parser.add_argument('--create-anonym-videos', action='store_true', help='Create anonymized videos')
parser.add_argument('--export-anonym-videos', action='store_true', help='Export anonymized videos')
parser.add_argument('--all', action='store_true', help='Run all operations')

args = parser.parse_args()

# --- Set Flags ---
RM_DB_SQLITE = args.rm_db or args.all
MIGRATE_DB = args.migrate or args.all
LOAD_BASE_DB_DATA = args.load_base_data or args.all
LOAD_MODEL = args.load_model or args.all
IMPORT_VIDEO = args.import_video or args.all
PREDICT_VIDEO = args.predict  # Don't automatically predict if --all is used unless --predict is also specified
VIDEO_NAME = args.video_name
CREATE_PSEUDO_EXAMINATIONS = args.create_pseudo_examinations or args.all
MODEL_NAME = "image_multilabel_classification_colonoscopy_default"  # Define model name centrally
CREATE_ANONYM_VIDEOS = args.create_anonym_videos or args.all
EXPORT_ANONYM_VIDEOS = args.export_anonym_videos or args.all

# --- Helper Function (Define locally) ---
def get_env_var(key):
    """Gets an environment variable and strips leading/trailing quotes."""
    value = os.getenv(key)
    if value:
        return value.strip('"\'') # Strip both single and double quotes
    return None

# --- Environment Setup & Django Initialization ---
print("Loading environment variables from .env file...")
settings_module = get_env_var('DJANGO_SETTINGS_MODULE') # Use the local function

print(f"DJANGO_SETTINGS_MODULE (raw): {os.getenv('DJANGO_SETTINGS_MODULE')}")
print(f"DJANGO_SETTINGS_MODULE (stripped): {settings_module}")

assert settings_module, "DJANGO_SETTINGS_MODULE not found or empty after stripping quotes."

# Set DJANGO_SETTINGS_MODULE environment variable *before* calling setup()
os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
print(f"Set os.environ['DJANGO_SETTINGS_MODULE'] = {os.environ['DJANGO_SETTINGS_MODULE']}")

# Configure Django settings
print("Calling django.setup()...")
try:
    django.setup()
    print("django.setup() completed successfully.")
except Exception as e:
    print(f"Error during django.setup(): {e}")
    raise

# --- Model Import (After django.setup) ---
from endoreg_db.models import AiModel, ModelMeta

# --- Paths (After django.setup if they depend on settings) ---
storage_dir = data_paths["storage"]
import_video_dir = data_paths["video_import"]

# --- Database Operations ---
if RM_DB_SQLITE:
    db_file = Path("db.sqlite3")
    if db_file.exists():
        try:
            result = subprocess.run(["rm", str(db_file)], check=True, capture_output=True)
            print("Database file removed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to remove database file: {e}")
            print(f"Error output: {e.stderr.decode('utf-8')}")
    else:
        print("Database file does not exist, skipping removal.")

# --- Django Management Commands ---
if MIGRATE_DB:
    print("Running migrate command...")
    out = call_command("migrate")
    print(out)

if LOAD_BASE_DB_DATA:
    print("Running load_base_db_data command...")
    out = call_command("load_base_db_data")
    print(out)

MODEL_TO_USE = None  # Variable to hold the model instance

if LOAD_MODEL:
    print("Calling create_multilabel_model_meta command...")
    MODEL_PATH_STR = "~/test-data/model/colo_segmentation_RegNetX800MF_6.ckpt"
    expanded_model_path = Path(MODEL_PATH_STR).expanduser().resolve()
    if not expanded_model_path.exists():
        raise FileNotFoundError(
            f"Model checkpoint not found at {expanded_model_path}. "
            "Update MODEL_PATH_STR or ensure the file is present."
        )
    print(f"Using model checkpoint: {expanded_model_path}")
    try:
        # First, ensure the AiModel exists or create it if necessary
        MODEL_TO_USE, created = AiModel.objects.get_or_create(
            name=MODEL_NAME,
            defaults={  # Provide defaults if creating a new AiModel
                'description': 'Default multilabel classification model for colonoscopy',
                'model_type': 'image_classification',  # Adjust if necessary
                'model_subtype': 'multilabel',  # Adjust if necessary
            }
        )
        if created:
            print(f"AiModel '{MODEL_NAME}' created.")
        else:
            print(f"AiModel '{MODEL_NAME}' found.")

        # Now, call the command to create the ModelMeta, ensuring it uses the correct model_name
        # The command should internally set the ModelMeta's name field correctly.
        print(f"Ensuring ModelMeta exists for AiModel '{MODEL_TO_USE.name}'...")
        out = call_command(
            "create_multilabel_model_meta",
            model_path=str(expanded_model_path),
            model_name=MODEL_NAME,  # Use model_name to link to the AiModel
        )
        print(out)
        # Re-fetch the model just to be sure, although it should be the same instance
        MODEL_TO_USE = AiModel.objects.get(name=MODEL_NAME)

    except Exception as e:  # Catch potential errors during AiModel get/create or command call
        print(f"ERROR during model loading/meta creation: {e}")
        MODEL_TO_USE = None # Ensure model_to_use is None if there was an error

if IMPORT_VIDEO:
    print("Calling import_video command...")
    video_to_import = import_video_dir / VIDEO_NAME
    print(f"Importing video: {video_to_import}")
    if not video_to_import.exists():
        print(f"ERROR: Video file not found at {video_to_import}")
    else:
        out = call_command("import_video", str(video_to_import))
        print(out)

if PREDICT_VIDEO:
    # If LOAD_MODEL failed above, model_to_use will be None here.
    # We still need to check if the AiModel exists in the DB before attempting prediction.
    if not MODEL_TO_USE:
        print(f"Attempting to retrieve model '{MODEL_NAME}' for prediction...")
        try:
            # Check if the AiModel exists, even if meta creation might have failed
            model_check = AiModel.objects.get(name=MODEL_NAME)
            print(f"AiModel '{MODEL_NAME}' found in DB.")
            # We set model_to_use here so the prediction step can proceed,
            # assuming the ModelMeta *might* exist from a previous run.
            MODEL_TO_USE = model_check
        except AiModel.DoesNotExist:
            print(f"ERROR: AiModel '{MODEL_NAME}' not found in the database. Cannot run prediction.")
            MODEL_TO_USE = None # Ensure it's None if AiModel doesn't exist

    # Proceed only if the AiModel exists
    if MODEL_TO_USE:
        print(f"Calling predict_raw_video_files command. It will use ModelMeta '{MODEL_NAME}' (likely latest version).")
        try:
            # The command itself will raise ModelMeta.DoesNotExist if it can't find the meta
            out = call_command("predict_raw_video_files")
            print(out)
        except ModelMeta.DoesNotExist as e:  
            print(f"ERROR: {e}. Did you forget to run --load-model?")  
    else:
        print("Skipping prediction because the required AiModel could not be found.")

if CREATE_PSEUDO_EXAMINATIONS:
    print("Creating pseudo examination...")
    try:
        out = call_command("create_pseudo_examinations")
        print(out)
    except Exception as e:
        print(f"ERROR during pseudo examination creation: {e}")

if CREATE_ANONYM_VIDEOS:
    print("Creating anonymized videos...")
    try:
        out = call_command("create_anonym_videos")
        print(out)
    except Exception as e:
        print(f"ERROR during anonymized video creation: {e}")

if EXPORT_ANONYM_VIDEOS:
    print("Exporting anonymized videos...")
    try:
        out = call_command("export_anonym_videos")
        print(out)
    except Exception as e:
        print(f"ERROR during anonymized video export: {e}")


