# endo-ai

## Pipeline

### Requirements

1. Create `.env` file

```env
DJANGO_SALT=HighlySecureSalt
```

2. Download TestData
   Access the shared "ColoReg" folder in our Nextcloud and copy the test-data directory to your home directory.

### Setup

_Environment_

- run `direnv allow`
  - will initially fail
  - run `init-env`
  - run `uv sync`
  - run `direnv reload`

_Database_

- (if pre-existing, run `rm db.sqlite3`)
- `python manage.py migrate`
- `python manage.py load_base_db_data`

_Import AI Model_
run `python manage.py create_multilabel_model_meta --model_path "~/test-data/model/colo_segmentation_RegNetX800MF_6.ckpt"`

_Import Report_
run `python manage.py import_report ~/test-data/report/lux-gastro-report.pdf`

_Import Video_
run `python manage.py import_video ~/test-data/video/lux-gastro-video.mp4`
-> Copy UUID of the created RawVideoFile, e.g.:

`Saved db_video_dir/c391b1d0-3e6a-4353-939c-07f02c667fea.mp4`
-> `c391b1d0-3e6a-4353-939c-07f02c667fea`

```zsh

```

_Predict Video_
**KNOWN ISSUE:**
If we need to download base models, the command needs to be run in devenv shell to find correct ca files
For ffmpeg to work, we also need to operate within devenv shell

run `devenv shell`
run `export RAW_VID_UUID=c391b1d0-3e6a-4353-939c-07f02c667fea`
run `python manage.py predict_raw_video_file --raw_video_uuid $RAW_VID_UUID`

_Remove Outside Regions_
**In Production, we will neeed to validate Predictions and migrate the pipeline to use annotations instead of predictions**

run `python manage.py censor_outside --raw_video_uuid $RAW_VID_UUID`

_Create Patients and Examinations from Sensitive Meta_
**In Production, we will create patients and examinations after validating patient names, dob, and examination date from the SensitiveMeta's RawPdfFile or RawVideoFile**

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
