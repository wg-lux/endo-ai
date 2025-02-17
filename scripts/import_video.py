from pathlib import Path
from agl_frame_extractor import VideoFrameExtractor

VIDEO_INPUT_DIR = Path("data/import/video")
VIDEO_FILE = VIDEO_INPUT_DIR / "NINJAU_S001_S001_T026.MOV"

vfe = VideoFrameExtractor(
    input_folder="data/videos",
    output_folder="data/frames",
    use_multithreading=True,
    image_format="jpg",
)


vfe.process_video(VIDEO_FILE.resolve().as_posix())
