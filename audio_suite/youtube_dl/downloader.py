import argparse
import os
import subprocess

FFMPEG_PATH = r"C:\Users\Noah Richey\Development Tools\ffmpeg.exe"
FFPROBE_PATH = os.path.join(os.path.dirname(FFMPEG_PATH), "ffprobe.exe")
output_folder = os.path.join(os.getcwd(), "downloads")

def download(url, output_path, is_playlist=False):
    command = [
        "yt-dlp",
        "-S",
        "vcodec:h264,res,acodec:aac",
        "--output",
        output_path,
        "--ffmpeg-location",
        FFMPEG_PATH,
    ]

    # if os.path.exists(FFPROBE_PATH):
    #     command.extend(["--ffprobe-location", FFPROBE_PATH])

    # Explicitly enforce playlist or single video behavior
    if is_playlist:
        command.append("--yes-playlist")
    else:
        command.append("--no-playlist")

    command.extend(["--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"])

    command.append(url)

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print("Download failed.")
        if result.stderr:
            print(result.stderr)
        return

    print("Output:", result.stdout)
    if result.stderr:
        print("Error:", result.stderr)


def download_list(filepath, audio_only, output_path):
    with open(filepath, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if line:
                download(line, audio_only, output_path, is_playlist=False)

def download_single(url: str):
    singles_folder = os.path.join(output_folder, "Singles")
    os.makedirs(singles_folder, exist_ok=True)
    download(url, os.path.join(singles_folder, "%(title)s.%(ext)s"), False)

def run_downloader(playlist_url: str):

    os.makedirs(output_folder, exist_ok=True)

    # Organize items into a subfolder named after the playlist title
    output_path = os.path.join(
        output_folder, "%(playlist_title)s", "%(playlist_index)s - %(title)s.%(ext)s"
    )

    download(playlist_url, output_path, is_playlist=True)