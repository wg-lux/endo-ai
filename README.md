# endo-ai

## Pipeline

### Requirements

1. Create `.env` file (See `./conf/default.env` as example)

2. Download TestData
   Access the shared "ColoReg" folder in our Nextcloud and copy the test-data directory to your home directory.

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
**In Production, we will neeed to validate Predictions and migrate the pipeline to use annotations instead of predictions**

run `python manage.py censor_outside --raw_video_uuid $RAW_VID_UUID`

_Create Patients and Examinations from Sensitive Meta_
**In Production, we will create patients and examinations after validating patient names, dob, and examination date from the SensitiveMeta's RawPdfFile or RawVideoFile**
run `python manage.py create_pseudo_patients`
run `python manage.py create_pseudo_examinations`

_Create Report File_
**In Production, we need to make sure that sensitive Meta of the RawPdfFile is already validated**
run `python manage.py create_anonym_reports`

_Create Video_
**In Production, we need to make sure that sensitive meta and Outside segments are validated**
run `python manage.py create_anonym_videos`

### ToDo

# Working With Specific Objects

## Video

- extract frames:

```python
from endoreg_db.models import Video
from icecream import ic
v = Video.objects.first()

# Extract basic Video Info
v.initialize_video_specs() # set fps, height, duration, width
v.sync_from_raw_video() # set predictions, readable_predictions, sequences, and some states from raw video file

v.extract_frames()
ic(v)

# get single frame
f = v.get_frame(50)
ic(f)
assert f.frame_number==50

# Get Video Label Segments
lss = v.label_video_segments.all()
ls = lss[0]
ic(ls)

# get annotations
annotations = f.get_classification_annotations()
annotations = f.get_classification_annotations_by_label_and_value()
annotations = f.get_classification_annotations_by_value()


# Get Predictions
# predictions =

ff = v.get_frame_range(10,15)


n_frames_db = v.get_frame_number()
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

endoreg_db_production/endoreg_db/models/data_file/base_classes/abstract_video.py
endoreg_db_production/endoreg_db/models/data_file/import_classes/raw_video.py
endoreg_db_production/endoreg_db/models/data_file/base_classes/utils.py

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

python manage.py import_video ~/test-data/video/lux-gastro-video.mp4

copy uuid of raw_video_file, e.g.
897703d7-a870-4c6c-a4a5-344ef52bc271

## Create a new ModelMeta Object

ModelMeta objects store the models weights file and Metadata like the used labelset.
They have a ForeignKey relationship to an AiModel. AiModel Objects store information about the type of model and how it is used to process videos (e.g., the VideoSegmentationLabelSet)

run:

```zsh
python manage.py create_multilabel_model_meta --model_path "./data/models/colo_segmentation_RegNetX800MF_6.ckpt"
```

## Predict Video

Use UUID from above

```zsh
python manage.py predict_raw_video_file --raw_video_uuid 897703d7-a870-4c6c-a4a5-344ef52bc271

```

## Create Anonymized Video

```zsh
python manage.py censor_outside --raw_video_uuid 695754bb-32ee-46bd-8beb-8cc36760adc1

```

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
- The BASE_API_URL is set in devenv.nix and also in settings_base.py and import in settings_dev/_init_.py, allowing API calls to switch between development (127.0.0.1:8000) and production (for future, for exmaple : www.demo.com). 