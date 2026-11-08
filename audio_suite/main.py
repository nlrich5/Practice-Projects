from youtube_dl.downloader import run_downloader
from audio_processing.audio_processor import process
from album_cleanup.album_cleaner import clean_album
from single_cleanup.singles_cleaner import clean_singles
from utils import clean
import argparse, os, shutil

src = r"C:\Users\Noah Richey\Coding\Practice-Projects\audio_suite\downloads"
dst = r"C:\Users\Noah Richey\Coding\Practice-Projects\audio_suite\album_cleanup\album\media"



def main():
    parser = argparse.ArgumentParser(description="Full audio suite")
    parser.add_argument("--yt_link", nargs="+", type=str, help="Link to playlist on Youtube")
    parser.add_argument("--artist", type=str, help="Default artist name")
    parser.add_argument("--album_title", type=str, help="Name of the album")
    parser.add_argument("-s", "--single", action="store_true", help="Flag for a list of singles instead of an album")

    args = parser.parse_args()

    if args.single:
        clean_singles()
    else:
        run_downloader(args.yt_link[0])
        process(src, dst)
        clean_album(args.artist, args.album_title)
        clean()

if __name__ == "__main__":
    main()