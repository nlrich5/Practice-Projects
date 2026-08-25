import argparse
import os
import subprocess

FFMPEG_PATH = r"C:\Users\Noah Richey\Development Tools\ffmpeg.exe"
FFPROBE_PATH = os.path.join(os.path.dirname(FFMPEG_PATH), "ffprobe.exe")
output_folder = os.path.join(os.getcwd(), "downloads")

def download(url, audio_only, output_path, is_playlist=False):
    command = [
        "yt-dlp",
        "-S",
        "vcodec:h264,res,acodec:aac",
        "--output",
        output_path,
        "--ffmpeg-location",
        FFMPEG_PATH,
    ]

    if os.path.exists(FFPROBE_PATH):
        command.extend(["--ffprobe-location", FFPROBE_PATH])

    # Explicitly enforce playlist or single video behavior
    if is_playlist:
        command.append("--yes-playlist")
    else:
        command.append("--no-playlist")

    # Add audio extraction flags if requested
    if str(audio_only).lower() == "y":
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="My PROG")
    parser.add_argument("-s", "--single", help="Single video URL")
    parser.add_argument("-p", "--playlist", help="Playlist URL")
    parser.add_argument("-l", "--list", help="Filepath to text file containing URLs")
    parser.add_argument("-a", "--audio_only", help="y/n")

    args = parser.parse_args()

    os.makedirs(output_folder, exist_ok=True)

    # Separate output directory based on audio vs video mode
    subfolder = "audio_only" if str(args.audio_only).lower() == "y" else "video"

    if args.single is not None:
        output_path = os.path.join(output_folder, subfolder, "%(title)s.%(ext)s")
        download(args.single, args.audio_only, output_path, is_playlist=False)

    elif args.playlist is not None:
        # Organize items into a subfolder named after the playlist title
        output_path = os.path.join(
            output_folder, subfolder, "%(playlist_title)s", "%(playlist_index)s - %(title)s.%(ext)s"
        )
        download(args.playlist, args.audio_only, output_path, is_playlist=True)

    elif args.list is not None:
        output_path = os.path.join(output_folder, subfolder, "%(title)s.%(ext)s")
        download_list(args.list, args.audio_only, output_path)

    else:
        print("Please select single (-s), playlist (-p), or list (-l).")