"""Sample Script to predict a frame using the trained model"""

import json
from pathlib import Path
from icecream import ic
from torchvision import transforms
import numpy as np
import ssl

from endo_ai.predictor.model_loader import MultiLabelClassificationNet

from endo_ai.predictor.predict import Classifier, sample_config
from endo_ai.predictor.inference_dataset import InferenceDataset
from endo_ai.predictor.postprocess import (
    concat_pred_dicts,
    make_smooth_preds,
    find_true_pred_sequences,
)


ic(ssl.get_default_verify_paths())

import ffmpeg

probe = ffmpeg.probe(
    "/home/admin/test-data/db_video_dir/138c846e-649a-40eb-84d6-633c99f7e704.mp4"
)

################################# UPDATE #################################
VIDEO_UUID = "68a175cd-a66b-4f23-b255-d423052ed613"
###########################################################################

TEST_RUN = False
N_TEST_FRAMES = 100
PRED_OUTPUT_PATH = f"./data/predictions_{VIDEO_UUID}.json"
READABLE_PRED_OUTPUT_PATH = f"./data/readable_predictions_{VIDEO_UUID}.json"
SEQUENCE_PRED_OUTPUT_PATH = f"./data/sequence_predictions_{VIDEO_UUID}.json"

FPS = 50
SMOOTH_WINDOW_SIZE_S = 1
MIN_SEQ_LEN_S = 0.5
BINARIZE_THRESHOLD = 0.5

data_folder = Path(f"~/test-data/db_frame_dir/{VIDEO_UUID}/").expanduser()


model_path = "./data/models/colo_segmentation_RegNetX800MF_6.ckpt"
paths = [p for p in data_folder.glob("*.jpg")]

crop_template = [0, 1080, 550, 1920 - 20]  # [top, bottom, left, right]


start_message = f"""
    This script is used to predict the labels of a video frame by frame.

    Config:
    - Model: {model_path}
    - Data folder: {data_folder}
    - Crop template: {crop_template}
    - Test run: {TEST_RUN}
    - Output path: {PRED_OUTPUT_PATH}
    - Readable output path: {READABLE_PRED_OUTPUT_PATH}
    - Number of frames: {len(paths)}
    - FPS: {FPS}
    - Smooth window size: {SMOOTH_WINDOW_SIZE_S}
    - Minimum sequence length: {MIN_SEQ_LEN_S}
    - Video UUID: {VIDEO_UUID}
    - Binary threshold: {BINARIZE_THRESHOLD}
"""

ic(start_message)

# frame names in format "frame_{index}.jpg"
indices = [int(p.stem.split("_")[1]) for p in paths]
path_index_tuples = list(zip(paths, indices))
# sort ascending by index
path_index_tuples.sort(key=lambda x: x[1])
paths, indices = zip(*path_index_tuples)

string_paths = [p.resolve().as_posix() for p in paths]
crops = [crop_template for _ in paths]

ic(f"Detected {len(paths)} frames")

if TEST_RUN:  # only use the first 10 frames
    ic(f"Running in test mode, using only the first {N_TEST_FRAMES} frames")
    paths = paths[:N_TEST_FRAMES]
    indices = indices[:N_TEST_FRAMES]
    string_paths = string_paths[:N_TEST_FRAMES]
    crops = crops[:N_TEST_FRAMES]

assert paths, f"No images found in {data_folder}"

ic(f"Found {len(paths)} images")

ds = InferenceDataset(string_paths, crops, config=sample_config)

ic(f"Dataset length: {len(ds)}")

# Get a sample image
sample = ds[0]
ic("Shape:", sample.shape)  # e.g., torch.Size([3, 716, 716])

unorm = transforms.Normalize(
    mean=[-m / s for m, s in zip(sample_config["mean"], sample_config["std"])],
    std=[1 / s for s in sample_config["std"]],
)

model = MultiLabelClassificationNet.load_from_checkpoint(  # pylint: disable=no-value-for-parameter
    checkpoint_path=model_path,
)
_ = model.cuda()
_ = model.eval()
classifier = Classifier(model, verbose=True)

predictions = classifier.pipe(string_paths, crops)
readable_predictions = [classifier.readable(p) for p in predictions]

with open(PRED_OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(classifier.get_prediction_dict(predictions, string_paths), f, indent=2)

with open(READABLE_PRED_OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(
        readable_predictions,
        f,
        indent=2,
        default=lambda o: int(o) if isinstance(o, np.int64) else o,
    )

ic("Predictions saved to", PRED_OUTPUT_PATH)
ic("Readable predictions saved to", READABLE_PRED_OUTPUT_PATH)

merged_predictions = concat_pred_dicts(readable_predictions)


smooth_merged_predictions = {}
for key in merged_predictions.keys():
    smooth_merged_predictions[key] = make_smooth_preds(
        prediction_array=merged_predictions[key],
        window_size_s=SMOOTH_WINDOW_SIZE_S,
        fps=FPS,
    )

binary_smooth_merged_predictions = {}
for key in smooth_merged_predictions.keys():
    binary_smooth_merged_predictions[key] = (
        smooth_merged_predictions[key] > BINARIZE_THRESHOLD
    )

sequence_dict = {}
for label, prediction_array in binary_smooth_merged_predictions.items():
    sequence_dict[label] = find_true_pred_sequences(prediction_array)

with open(SEQUENCE_PRED_OUTPUT_PATH, "w") as f:
    json.dump(
        sequence_dict,
        f,
        indent=2,
        default=lambda o: int(o) if isinstance(o, np.int64) else o,
    )

ic("Sequence predictions saved to", SEQUENCE_PRED_OUTPUT_PATH)
