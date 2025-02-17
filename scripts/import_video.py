from pathlib import Path
from agl_frame_extractor import VideoFrameExtractor

VIDEO_INPUT_DIR = Path("~/test-data/video")
VIDEO_FILE = VIDEO_INPUT_DIR / "NINJAU_S001_S001_T029.MOV"

vfe = VideoFrameExtractor(
    input_folder="data/videos",
    output_folder="data/frames",
    use_multithreading=True,
    image_format="jpg",
)

# Transcode the input video if needed.
transcoded_file = vfe.transcode_video(VIDEO_FILE.resolve().as_posix())
# Extract frames from the transcoded video.
vfe.process_video(transcoded_file)
