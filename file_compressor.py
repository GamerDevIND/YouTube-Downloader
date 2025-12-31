import subprocess
import pathlib
from configs import ffmpeg_location

def compress_audio(input_path):
    input_path = pathlib.Path(input_path)
    output_path = input_path.with_name(input_path.stem + "_compressed" + input_path.suffix)
    
    if input_path.suffix.lower() in [".wav", ".flac"]:
        subprocess.run([
            ffmpeg_location,
            "-i", str(input_path),
            "-compression_level", "12",
            str(output_path)
        ], check=True)
    else:
        subprocess.run([
            ffmpeg_location,
            "-i", str(input_path),
            "-b:a", "192k",
            str(output_path)
        ], check=True)
    return output_path

def compress_mp4(input_path):
    output_path = pathlib.Path(input_path).with_name(
        pathlib.Path(input_path).stem + "_compressed.mp4"
    )
    subprocess.run([
       ffmpeg_location,
        "-i", str(input_path),
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18", 
        "-c:a", "copy",
        str(output_path)
    ], check=True)
    return output_path
