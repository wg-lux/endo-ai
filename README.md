# endo-ai

## Pipeline

### Requirements

1. Create `.env` file (See `./conf/default.env` as example)

2. Download TestData
   Access the shared "ColoReg" fwwolder in our Nextcloud and copy the test-data directory to your home directory.

### Setup

_Environment_

- run `direnv allow`
  - might initially fail
  - run `uv sync`
  - run `init-env`
  - run `direnv reload`

### Demo

_Note: create a .env file using the template `./conf_template/default.env` and modify it as required_

- run `devenv shell`
- run `demo-pipe`

_Remove Outside Regions_
**In Production, we will need to validate Predictions and migrate the pipeline to use annotations instead of predictions**

run `python manage.py censor_outside --video_uuid $VIDEO_UUID` # Use VideoFile UUID

_Create Patients and Examinations from Sensitive Meta_
**In Production, we will create patients and examinations after validating patient names, dob, and examination date from the SensitiveMeta's RawPdfFile or VideoFile**
run `python manage.py create_pseudo_patients`
run `python manage.py create_pseudo_examinations`

_Create Report File_
**In Production, we need to make sure that sensitive Meta of the RawPdfFile is already validated**
run `python manage.py create_anonym_reports`

_Create Anonymized Video_
**In Production, we need to make sure that sensitive meta and Outside segments are validated**
run `python manage.py create_anonym_videos --video_uuid $VIDEO_UUID` # Use VideoFile UUID

### ToDo

- autodocs / Sphinx
- add labelset: "gg-pilot-paris", "gg-pilot-nice"
- add labels for those labelsets
- annotation should allow for "i dont know / skip" and "no polyp"

- Autoselect 1 polyp image per sequence per second (more or less random)
  - should not have label "outside"
  - EXTRA: 1 with predicted label nbi and one without predicted label nbi
  - Use the image with nbi for annotation of NICE classification
  - Use the image without nbi for annotation of Paris classification

To close the loop until re-training:

- Create script which automatically sets the label "polyp" to true in each \
  image with a annotation for one the NICE / Paris labels

# Working With Specific Objects

## VideoFile

```python
from endoreg_db.models import VideoFile
from icecream import ic
v = VideoFile.objects.first() # Get a VideoFile instance

# Access files
raw_path = v.raw_file.path if v.has_raw else None
processed_path = v.processed_file.path if v.is_processed else None
active_path = v.active_file_path

ic(raw_path, processed_path, active_path)

# Extract basic Video Info (from raw file initially)
v.update_video_meta() # Populates VideoMeta from raw file if needed
v.initialize_video_specs() # Populates fps, width, etc. from active file if needed

# Extract frames (from raw file)
v.extract_frames()
ic(v.state.frames_extracted)

# get single frame
f = v.get_frame(50)
ic(f)
assert f.frame_number==50

# Get Video Label Segments (linked to this VideoFile)
lss = v.label_video_segments.all()
ls = lss[0] if lss else None
ic(ls)

# get annotations for a frame
annotations = f.get_classification_annotations()
# ... other annotation methods ...

# Get frame count
n_frames_db = v.get_frame_number() # Counts Frame objects
n_frames_meta = v.frame_count # From VideoMeta

# Predict
# Ensure model meta exists first
v.predict_video(model_meta_name="your_model_name")
ic(v.sequences) # Check predicted sequences stored on the instance
ic(v.state.initial_prediction_completed)
ic(v.state.lvs_created)

# Anonymize
if v.has_raw and not v.is_processed:
    processed_video_path = v.anonymize(delete_original_raw=True)
    ic(processed_video_path)
    ic(v.is_processed)
    ic(v.has_raw) # Should be False if delete_original_raw=True
    ic(v.active_file_path) # Should now point to processed file
```

## Notes

ToDo:

- autodocs / Sphinx
- add labelset: "gg-pilot-paris", "gg-pilot-nice"
- add labels for those labelsets
- annotation should allow for "i dont know / skip" and "no polyp"

- Autoselect 1 polyp image per sequence per second (more or less random)
  - should not have label "outside"
  - EXTRA: 1 with predicted label nbi and one without predicted label nbi
  - Use the image with nbi for annotation of NICE classification
  - Use the image without nbi for annotation of Paris classification

To close the loop until re-training:

- Create script which automatically sets the label "polyp" to true in each \
  image with a annotation for one the NICE / Paris labels

## Important Methods / Files / Classes

Create ".env"

```env
DJANGO_SALT=YourSecureSalt
```

DJANGO_SALT is used to generate hashes.
If it changes, generated hashes will differ and new reports of existing patients wont be mergable with existing hashes.

`endoreg_db/models/media/video/video_file.py` # The main consolidated video model
`endoreg_db/models/media/frame/frame.py`
`endoreg_db/models/label/label_video_segment.py`
`endoreg_db/models/metadata/video_prediction_meta.py`
`endoreg_db/models/state/video.py`
`endoreg_db/models/media/video/helpers.py`
`endoreg_db/models/media/video/predict_video.py`
`endoreg_db/models/media/video/create_from_file.py`
`endoreg_db/models/utils.py`

## Requirements

model file at: './data/models/colo_segmentation_RegNetX800MF_6.ckpt'

test video at: '~/test-data/video/lux-gastro-video.mp4'

/home/admin/test-data/video/lux-gastro-video.mp4

## Prepare sqlite database

We use settings_dev and therefore the local sqlite db file.

For a clean testing run, delete the existing db.sqlite3 file and create a new one

```zsh
rm db.sqlite3
init-data
```

## Import Video

`python manage.py import_video ~/test-data/video/lux-gastro-video.mp4`

copy uuid of the created `VideoFile`, e.g.
`897703d7-a870-4c6c-a4a5-344ef52bc271`

## Create a new ModelMeta Object

ModelMeta objects store the models weights file and Metadata like the used labelset.
They have a ForeignKey relationship to an AiModel. AiModel Objects store information about the type of model and how it is used to process videos (e.g., the VideoSegmentationLabelSet)

run:

```zsh
python manage.py create_multilabel_model_meta --model_path "./data/models/colo_segmentation_RegNetX800MF_6.ckpt"
```

## Predict Video

Use `VideoFile` UUID from above

```zsh
python manage.py predict_video --video_uuid 897703d7-a870-4c6c-a4a5-344ef52bc271 --model_name your_model_name
```

## Censor Outside Frames (Optional Pre-Anonymization Step)

```zsh
python manage.py censor_outside --video_uuid 897703d7-a870-4c6c-a4a5-344ef52bc271
```

## Create Anonymized Video

```zsh
python manage.py create_anonym_videos --video_uuid 897703d7-a870-4c6c-a4a5-344ef52bc271
```
This command will internally call the `video_file.anonymize()` method.

## Generate ReportFile from RawPdfFile

#####

## set active model meta

python manage.py set_active_meta --model_name image_multilabel_classification_colonoscopy_default

## Generate VideoObject with Pseudo ID Object

- during generation we assign a model meta
- by default we use the active model
- we predict using the generated anonymized frames from the raw video file
- we store the video segments and the corresponding raw prediction matrix

## Create VideoSegmentAnnotations from Predictions

## Use Outside Segments to completely black out corresponding frames

## Create Anonymized Video

## Read Raw Report

## Raw Report to Report with Pseudo ID Object

## Tmux Remote Session

### 1. Start new named tmux session

tmux new -s endo-ai

### 2. Start your long-running task inside tmux

python manage.py import_video /path/to/video.mp4

### 3. Detach from session (while inside tmux)

Press Ctrl+b then d

# 4. List existing sessions

tmux ls

# 5. Reattach to session later

tmux attach -t endo-ai

# Optional: Kill session when done

tmux kill-session -t endo-ai

## Possible Errors
- `Module not found` error detected. Check the `.env` and `./conf/default.env` files for missing or incorrect configurations.

## BASE_API_URL
- The BASE_API_URL is set in devenv.nix and also in settings_base.py and import in settings_dev/_init_.py, allowing API calls to switch between development (127.0.0.1:8000) and production (for future, for example: www.demo.com).