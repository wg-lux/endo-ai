"""Sample Script to predict a frame using the trained model"""

from pathlib import Path
from icecream import ic
from PIL import Image
from torchvision import transforms

from endo_ai.predictor.model_loader import MultiLabelClassificationNet

from endo_ai.predictor.predict import Classifier, sample_config
from endo_ai.predictor.inference_dataset import InferenceDataset

import ssl

ic(ssl.get_default_verify_paths())


FPS = 50
SMOOTH_WINDOW_SIZE_S = 1
MIN_SEQ_LEN_S = 0.5

data_folder = Path("./data/test_frames")
model_path = "./data/models/colo_segmentation_RegNetX800MF_6.ckpt"
paths = [p for p in data_folder.glob("*.jpg")]

crop_template = [0, 1080, 550, 1920 - 20]  # [top, bottom, left, right]

# frame names in format "frame_{index}.jpg"
indices = [int(p.stem.split("_")[1]) for p in paths]
path_index_tuples = list(zip(paths, indices))
# sort ascending by index
path_index_tuples.sort(key=lambda x: x[1])
paths, indices = zip(*path_index_tuples)

string_paths = [p.resolve().as_posix() for p in paths]

crops = [crop_template for _ in paths]

assert paths, f"No images found in {data_folder}"

ic(f"Found {len(paths)} images")
ic(f"First image: {paths[0]}, Index: {indices[0]}")

ds = InferenceDataset(string_paths, crops, config=sample_config)

ic(f"Dataset length: {len(ds)}")

# Get a sample image
sample = ds[0]
ic("Shape:", sample.shape)  # e.g., torch.Size([3, 716, 716])

unorm = transforms.Normalize(
    mean=[-m / s for m, s in zip(sample_config["mean"], sample_config["std"])],
    std=[1 / s for s in sample_config["std"]],
)

# save the sample image to datafolder / sample.jpg
sample_unnorm = unorm(sample.clone())
sample_img = sample_unnorm.permute(1, 2, 0).numpy()
sample_img = (sample_img * 255).clip(0, 255).astype("uint8")
sample_img = Image.fromarray(sample_img)
sample_img.save(data_folder / "test_outputs/sample.jpg")


model = MultiLabelClassificationNet.load_from_checkpoint(  # pylint: disable=no-value-for-parameter
    checkpoint_path=model_path,
)
_ = model.cuda()
_ = model.eval()
classifier = Classifier(model, verbose=True)

predictions = classifier.pipe(string_paths, crops)
readable_predictions = [classifier.readable(p) for p in predictions]

# save to datafolder / predictions.txt
with open(data_folder / "test_outputs/predictions.txt", "w", encoding="utf-8") as f:
    for p in readable_predictions:
        f.write(str(p) + "\n\n")  # changed: convert dict to string before concatenation

ic(readable_predictions)
