import os, shutil, subprocess, traceback
from pydub import AudioSegment

ffmpeg_dir = r"C:\Users\Noah Richey\Development Tools"

# print("Folder exists:", os.path.isdir(ffmpeg_dir))
# print("Contents:", os.listdir(ffmpeg_dir) if os.path.isdir(ffmpeg_dir) else None)

os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
TARGET = -14.0 

def process(src: str, dst: str):
    os.makedirs(dst, exist_ok=True)

    for root, dirs, files in os.walk(src):
        for file in files:
            if not file.lower().endswith(".mp3"):
                continue
            audio = AudioSegment.from_mp3(os.path.join(root, file))
            if audio.dBFS < TARGET:
                adjusted = audio.apply_gain(TARGET - audio.dBFS)
                adjusted.export(os.path.join(dst, file), format="mp3", bitrate="320k")
                print(f"{file}: {audio.dBFS:.1f} -> {adjusted.dBFS:.1f} dBFS")
            else:
                shutil.copy2(os.path.join(root, file), dst)
                print(f"{file}: {audio.dBFS:.1f} -> {audio.dBFS:.1f} dBFS")