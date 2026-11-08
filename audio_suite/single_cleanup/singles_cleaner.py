import re
import shutil
import sys, os
import csv
from dataclasses import dataclass
from pathlib import Path
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1, TRCK, TALB
from mutagen.mp3 import MP3

from youtube_dl.downloader import download_single
from audio_processing.audio_processor import process
from utils import clean

@dataclass
class Track:
	number: int
	title: str
	artist: str

media_path = r"C:\Users\Noah Richey\Coding\Practice-Projects\audio_suite\downloads\Singles"
dst = r"C:\Users\Noah Richey\Coding\Practice-Projects\audio_suite\album_cleanup\album\media"

def write_tags(media_path: Path, title: str, artist: str, number: int, album_title: str) -> None:
	try:
		tags = ID3(media_path)
	except ID3NoHeaderError:
		tags = ID3()
	tags["TIT2"] = TIT2(encoding=3, text=title)
	tags["TPE1"] = TPE1(encoding=3, text=artist)
	tags["TRCK"] = TRCK(encoding=3, text=str(number))
	tags["TALB"] = TALB(encoding=3, text=album_title)
	tags.save(media_path)

def clean_singles():
	tracks: list[Track] = []
	
	with open("./single_cleanup/singles.csv", "r", encoding="utf-8") as f:
		reader = csv.DictReader(f)
		for row in reader:
			download_single(row["Link"])
			
			files = os.listdir(media_path)
			media_file = files[0]
			process(media_path, dst)
			dst_fp = os.path.join(dst, media_file)
			write_tags(dst_fp, row["Title"], row["Artist"], 1, row["Album"])
			clean()
			
			print(f"{media_file} processed and moved")