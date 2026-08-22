import subprocess
import os


def video_audio(folder_path):
    list_files = os.listdir(folder_path)
    os.makedirs("audio", exist_ok=True)
    for video_file in list_files:
        file = video_file.split(".")[0]
        command = [
        "ffmpeg",
        "-y",
        "-i", f"{folder_path}/{video_file}",   # input file
        "-q:a", "0",        # audio quality (0 = best)
        "-map", "a",        # select only audio stream
        f"audio/{file}.mp3"
        ]
        subprocess.run(command, check=True)
    return "Conversion Complete"