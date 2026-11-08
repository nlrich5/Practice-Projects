import re
import sys
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1, TRCK, TALB
from mutagen.mp3 import MP3

html_path = r"C:\Users\Noah Richey\Coding\Practice-Projects\audio_suite\album_cleanup\album\html\downloaded.html"
media_path = r"C:\Users\Noah Richey\Coding\Practice-Projects\audio_suite\album_cleanup\album\media"

if hasattr(sys.stdout, "reconfigure"):
	sys.stdout.reconfigure(errors="backslashreplace")


@dataclass
class Track:
	number: int
	title: str
	artist: str


def normalized(value: str) -> str:
	return re.sub(r"[^a-z0-9]", "", value.casefold())

def extract_tracks(html_path: Path) -> list[Track]:
	print(f"HTML: {html_path}")
	soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
	tracks: list[Track] = []
	number_offset = 0
	for table in soup.select("table.tbl.medium"):
		table_tracks = []
		for row in table.select("tr[id]"):
			cells = row.find_all("td", recursive=False)
			if len(cells) < 3:
				continue
			number_text = cells[0].get_text(strip=True)
			if not re.fullmatch(r"\d+", number_text):
				continue
			title_link = cells[1].find("a")  # first link is the title; credits come after it
			if title_link is None:
				continue
			title = title_link.get_text(" ", strip=True)
			artist = cells[2].get_text(" ", strip=True)
			if title and artist:
				table_tracks.append(Track(int(number_text) + number_offset, title, artist))
		tracks.extend(table_tracks)
		if table_tracks:
			number_offset = max(track.number for track in table_tracks)
	if not tracks:
		raise ValueError("Could not find a track list in the MusicBrainz HTML.")
	return tracks


def match_track(media_path: Path, tracks: list[Track]) -> Track:
	filename_key = normalized(media_path.stem)
	candidates = [track for track in tracks if normalized(track.title) in filename_key]
	file_number = re.match(r"\s*(\d+)", media_path.stem)
	if file_number:
		numbered = [track for track in candidates if track.number == int(file_number.group(1))]
		if numbered:
			return numbered[0]
		if candidates:
			raise ValueError(f"The track number in '{media_path.name}' conflicts with its matching title.")
	if len(candidates) == 1:
		return candidates[0]
	if not candidates:
		raise ValueError(f"No track title in the HTML matches '{media_path.name}'.")
	names = ", ".join(track.title for track in candidates)
	raise ValueError(f"'{media_path.name}' could match multiple tracks ({names}); include the track number in its filename.")


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


def clean_album(artist: str, album_title: str):
	media_inputs = []
	path = Path(media_path)
	if not path.exists():
		raise ValueError(f"Media path does not exist: {path}")
	if path.is_dir():
		media_dir = Path(media_path)
		media_inputs = [
			(child, True)
			for child in sorted(
				(child for child in media_dir.iterdir()
				if child.is_file() and child.suffix.casefold() == ".mp3"),
				key=lambda child: child.name.casefold(),
			)
		]
	elif path.is_file():
		if path.suffix.casefold() != ".mp3":
			raise ValueError(f"Only MP3 files are supported: {path}")
		media_inputs.append((path, False))
	else:
		raise ValueError(f"Media path must be an MP3 file or folder: {path}")
	if not media_inputs:
		raise ValueError("No MP3 files found in the supplied media paths.")

	try:
		tracks = extract_tracks(Path(html_path))
		matched = []
		for path, from_folder in media_inputs:
			try:
				matched.append((path, match_track(path, tracks)))
			except ValueError as error:
				if not from_folder:
					raise
				print(f"Skipping {path}: {error}", file=sys.stderr)
		if not matched:
			raise ValueError("No supplied media files matched the track list.")
	except (OSError, ValueError) as error:
		print(f"Error: {error}", file=sys.stderr)
		return 1

	for path, track in matched:
		print(f"{path}: {track.title} | {artist or track.artist}")

	for path, track in matched:
		try:
			MP3(path)
			write_tags(path, track.title, artist or track.artist, track.number, album_title)
		except Exception as error:
			print(f"Error tagging {path}: {error}", file=sys.stderr)
			return 1
	print(f"Tagged {len(matched)} file(s).")
	return 0