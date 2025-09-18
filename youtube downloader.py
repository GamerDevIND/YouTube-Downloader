import yt_dlp
import os
import time

vid_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': './assets/ffmpeg.exe',
    'no_mtime': True,
    'nocache': False,
    'merge_output_format': 'mp4',
    "quiet": True,
    "cachedir": "./cache",
    'cookiefile': './assets/youtube.com_cookies.txt',
    'concurrent_fragment_downloads': 128,
}

audio_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': './assets/ffmpeg.exe',
    'no_mtime': True,
    'nocache': False,
    "quiet": True,
    'cookiefile': './assets/youtube.com_cookies.txt',
    'concurrent_fragment_downloads': 256,
    "cachedir": "./cache",
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320'
        },
    ],
}

audio_fallback_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': './assets/ffmpeg.exe',
    'no_mtime': True,
    'nocache': False,
    'cookiefile': './assets/youtube.com_cookies.txt',
    'concurrent_fragment_downloads': 64,
    "cachedir": "./cache",
    "quiet": True,
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        },
    ],
}

video_fallback_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': './assets/ffmpeg.exe',
    'no_mtime': True,
    'nocache': False,
    "cachedir": "./cache",
    "quiet": True,
    'cookiefile': './assets/youtube.com_cookies.txt',
    'concurrent_fragment_downloads': 32,
    'merge_output_format': 'mp4',
}

search_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': './assets/ffmpeg.exe',
    'quiet': True,
    'noplaylist': True,
    'nocache': False,
    'extract_flat': True,
    "cachedir": "./cache",
    'concurrent_fragment_downloads': 256,
}


if not os.path.exists("./cache"):
    os.mkdir("./cache")
if not os.path.exists("./assets"):
    os.mkdir("./assets")
    print("Please add \n'ffmpeg.exe'\nand\n'youtube.com_cookies.txt' files to continue")
    exit(1)

def loader(d):
    if d['status'] == 'downloading':
        print(f"\r[>] Downloading: {d['_percent_str']} @ {d['_speed_str']}", end='')
    elif d['status'] == 'finished':
        print("\n[=] Done!")


def search(query, total_search=5):
    print(f"[O] Searching '{query}'...\n")
    with yt_dlp.YoutubeDL(search_opts) as searcher:
        results = searcher.extract_info(f"ytsearch{total_search}:{query}", download=False)
        return results['entries'] # type: ignore

def download(url, only_audio=True):
    options = audio_opts if only_audio else vid_opts
    options["progress_hooks"] = [loader]
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"[!] Initial download try failed: {e}")
        print("[!] Trying fallback...")
        fallback_options = audio_fallback_opts if only_audio else video_fallback_opts
        try:
            with yt_dlp.YoutubeDL(fallback_options) as fallback:
                fallback.download([url])
        except Exception as e2:
            print(f"[X] Fallback also failed: {e2}")
            print("Skipping this item")

s = time.time()
search_url = input("do you have the url of the video? (Y/N)").lower()
if search_url == "n":
    results = search(input("Enter search query: ").strip() or "YouTube")

    for idx, vid in enumerate(results):
        print(f"{idx}. {vid['title']} (- {vid['channel']})")

    print()
    choice = int(input("Enter choice: "))

    vid_id = results[choice]["id"]
    url = f"https://www.youtube.com/watch?v={vid_id}"

    print(f"\n[O] Downloading: {results[choice]['title']} (- {results[choice]['channel']})\n")
else:
    url = input("Enter URL: ")

a = input("Download only Audio (A) or Video with audio (V)?: ").strip().lower()
while a not in ('a', 'v'):
    a = input("[!] Invalid choice. Please enter 'A' or 'V': ").strip().lower()

download(url, a == "a")

print(f"\n[.] Total time: {time.time() - s:.2f} seconds")
