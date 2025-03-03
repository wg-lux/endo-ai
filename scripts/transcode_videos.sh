#!/usr/bin/env zsh
# Check for directory argument

# Example Usage

if [ $# -lt 1 ]; then
  echo "Usage: $0 <directory-path>"
  exit 1
fi

target_dir="$1"
if [ ! -d "$target_dir" ]; then
  echo "Directory $target_dir does not exist."
  exit 1
fi

# Enable null_glob to avoid literal pattern if no files found
setopt null_glob
mov_files=("$target_dir"/*.mov "$target_dir"/*.MOV)
unsetopt null_glob

if [ ${#mov_files[@]} -eq 0 ]; then
  echo "No .mov or .MOV files found in $target_dir."
  exit 0
fi

for file in "${mov_files[@]}"; do
  out_file="${file%.*}.mp4"
  echo "Transcoding $file to $out_file..."
  ffmpeg -y -i "$file" -c:v libx264 -crf 22 -preset slow -c:a aac -b:a 192k "$out_file"
done

echo "Transcoding completed."
