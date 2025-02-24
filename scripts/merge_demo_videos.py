from pathlib import Path
import subprocess
from icecream import ic

SOURCE_DIR = Path("data/demo")

# get all .mp4 files
video_files = list(SOURCE_DIR.glob("*.mp4"))

# make sure that we have only 2
if len(video_files) > 2:
    ic(f"Waring: Found more than 2 videos in {SOURCE_DIR}, using only the first 2")
elif len(video_files) < 2:
    raise ValueError(
        f"Found less than 2 videos in {SOURCE_DIR}, please provide 2 videos"
    )

output_file = Path("data/demo/output.mp4")

# Render a new video by playing both videos side by side
# Rescale final output to 720p

cmd = [
    "ffmpeg",
    "-y",
    "-i",
    str(video_files[0]),
    "-i",
    str(video_files[1]),
    "-filter_complex",
    "[0:v]scale=-2:720[v0];[1:v]scale=-2:720[v1];[v0][v1]hstack=inputs=2[v]",
    "-map",
    "[v]",
    "-c:v",
    "libx264",
    "-crf",
    "23",
    "-preset",
    "veryfast",
    str(output_file),
]

subprocess.run(cmd, check=True)

print(f"Created side-by-side video at {output_file}")
