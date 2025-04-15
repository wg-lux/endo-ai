import os
from pathlib import Path
import dotenv
dotenv.load_dotenv()
import argparse
import subprocess
import django
from django.core.management import call_command
from endoreg_db.utils.paths import data_paths

# --- Example Usage ---
# python scripts/process_video.py --rm-db --migrate --load-base-data --load-model --import-video --video-name NINJAU_S001_S001_T018.mp4

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description='Process video and manage database operations.')
parser.add_argument('--rm-db', action='store_true', help='Remove SQLite database')
parser.add_argument('--migrate', action='store_true', help='Run database migrations')
parser.add_argument('--load-base-data', action='store_true', help='Load base data into database')
parser.add_argument('--load-model', action='store_true', help='Load AI model')
parser.add_argument('--import-video', action='store_true', help='Import video file')
parser.add_argument('--video-name', default="NINJAU_S001_S001_T018.mp4", help='Name of video file to import')
parser.add_argument('--all', action='store_true', help='Run all operations')
args = parser.parse_args()

# --- Set Flags ---
RM_DB_SQLITE = args.rm_db or args.all
MIGRATE_DB = args.migrate or args.all
LOAD_BASE_DB_DATA = args.load_base_data or args.all
LOAD_MODEL = args.load_model or args.all
IMPORT_VIDEO = args.import_video or args.all
VIDEO_NAME = args.video_name

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
from endoreg_db.models import AiModel

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

if LOAD_MODEL:
    print("Calling create_multilabel_model_meta command...")
    model_path_str = "~/test-data/model/colo_segmentation_RegNetX800MF_6.ckpt"
    expanded_model_path = Path(model_path_str).expanduser().resolve()
    print(f"Expanded Model Path: {expanded_model_path}")
    try:
        model = AiModel.objects.get(name="image_multilabel_classification_colonoscopy_default")
        print(f"Model found: {model}")
    except AiModel.DoesNotExist:
        print(f"Model not found in the database. Proceeding to create a new one.")
        out = call_command(
            "create_multilabel_model_meta",
            model_path=str(expanded_model_path),
        )
        print(out)

if IMPORT_VIDEO:
    print("Calling import_video command...")
    video_to_import = import_video_dir / VIDEO_NAME
    print(f"Importing video: {video_to_import}")
    if not video_to_import.exists():
        print(f"ERROR: Video file not found at {video_to_import}")
    else:
        out = call_command("import_video", str(video_to_import))
        print(out)

