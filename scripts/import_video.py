from pathlib import Path
from endoreg_db.models import RawVideoFile
from agl_frame_extractor import VideoFrameExtractor


VIDEO_INPUT_DIR = Path("~/test-data/video").expanduser()
VIDEO_FILE = VIDEO_INPUT_DIR / "NINJAU_S001_S001_T029.MOV"

FRAME_EXTRACTOR_DATA_DIR = Path("~/test-data/frame-extractor").expanduser()
FRAME_EXTRACTOR_DATA_DIR.mkdir(exist_ok=True)


# vfe = VideoFrameExtractor(
#     input_folder=VIDEO_INPUT_DIR.resolve().as_posix(),
#     output_folder=FRAME_EXTRACTOR_DATA_DIR.resolve().as_posix(),
#     use_multithreading=True,
#     image_format="jpg",
# )

# # Extract frames and metadata from the video.
# vfe.extract_frames_and_metadata()
