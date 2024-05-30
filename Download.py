import os
import threading
import time
from queue import Queue

from pip._internal.cli.cmdoptions import progress_bar
from pytube import Playlist, YouTube
from tqdm import tqdm
from tkinter import Tk, filedialog


def download_video(video_url, idx, progress_bar,download_dir):
    try:
        # Create a YouTube object
        yt = YouTube(video_url)

        # Get the highest resolution stream
        stream = yt.streams.get_highest_resolution()

        # Get the filename
        filename = os.path.join(download_dir, stream.default_filename)
        print(f"\nDownloading video : {yt.title} \t({idx}/{len(video_urls)})\n")
        start_time = time.time()
        # Check if the file exists in the current directory
        if not os.path.exists(filename):
            # Download the video
            # print(f"Downloading video {idx}: {yt.title} {video_url}")
            stream.download(output_path=download_dir)
            # progress_bar.write(f"{GREEN_COLOR}Video {idx} downloaded successfully!{RESET_COLOR}")
            # Track end time
            end_time = time.time()
            # Calculate download speed and time elapsed
            download_speed = os.path.getsize(filename) / (end_time - start_time) / (1024 * 1024)  # in MB/s
            time_elapsed = end_time - start_time  # in seconds
            print(
                f"{GREEN_COLOR}Video  {yt.title} downloaded successfully! (Speed: {download_speed:.2f} MB/s, Time Elapsed: {time_elapsed:.2f} seconds) ({idx}/{len(video_urls)}). {RESET_COLOR}")
        else:
            print(
                f"{ORANGE_COLOR}Video {yt.title}  already exists in the directory {download_dir} {idx} / {len(video_urls)}.{RESET_COLOR}")

    except Exception as e:
        print(f"{RED_COLOR}Error downloading video {idx}: {e}{RESET_COLOR}")


def worker(progress_bar,download_dir):
    while True:
        item = q.get()
        if item is None:
            break
        download_video(*item, progress_bar,download_dir)
        q.task_done()


# Function to choose the download directory
def choose_download_dir():
    root = Tk()
    root.withdraw()  # Hide the main window
    download_dir = filedialog.askdirectory(title="Choose Download Directory")
    root.destroy()  # Destroy the main window
    return download_dir


# ANSI escape code for red color
RED_COLOR = "\033[91m"
RESET_COLOR = "\033[0m"
# ANSI escape codes for colors
GREEN_COLOR = "\033[92m"
ORANGE_COLOR = "\033[33m"
# YouTube playlist URL
playlist_url = 'https://www.youtube.com/playlist?list=PLHIfW1KZRIfkDF2xTIB5kX8gdthmLTufx'

# Create a Playlist object

playlist = Playlist(playlist_url)

# Get all video URLs in the playlist
video_urls = playlist.video_urls

# Choose the download directory
download_dir = choose_download_dir()
if download_dir == "":
    download_dir = "C:/Users/MNE/Videos/C#"
if download_dir:
    # Create a queue
    print(f"{GREEN_COLOR}selected dir:  {download_dir} !{RESET_COLOR}")
    # Create a queue
    q = Queue()

    # Create worker threads
    num_threads = 4
    threads = []
    for _ in range(num_threads):
        #t = threading.Thread(target=worker)
        t = threading.Thread(target=worker, args=(
            tqdm(total=len(video_urls), desc="Downloading", unit=" video", dynamic_ncols=True),download_dir))

        t.start()
        threads.append(t)

    # Add tasks to the queue
    for idx, video_url in enumerate(video_urls, start=1):

        if idx >= 708:
            print(idx)
            q.put((video_url, idx))

    # Wait for all tasks to be completed
    q.join()

    # Stop the worker threads
    for _ in range(num_threads):
        q.put(None)
    for t in threads:
        t.join()

    print("All videos downloaded.")

else:
    print("Download directory not selected. Exiting.")
