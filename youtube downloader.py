import yt_dlp
import os
import time
from configs import ffmpeg_location, ffprobe_location, cookies_location
from file_compressor import compress_audio, compress_mp4

vid_opts = {
    'format':'bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best[vcodec^=avc1]/best',
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': ffmpeg_location,
    'ffprobe_location':ffprobe_location,
    'no_mtime': True,
    'nocache': False,
    'merge_output_format': 'mp4',
    "quiet": True,
    "cachedir": "./cache",
    'cookiefile':cookies_location,
    'concurrent_fragment_downloads': 256,
    "embedsubtitles": True,
}

subtitles = { # download any subtitles if available preferredly VTT in English.
    "writesubtitles": True,
    "subtitleslangs": ["en.*"],
    "convertsubtitles": "srt",
    'subtitlesformat': "vtt/srt",
    "embedsubtitles": True,
    "embedsubtitles": True,
}

audio_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': ffmpeg_location,
    'ffprobe_location':ffprobe_location,
    'no_mtime': True,
    'nocache': False,
    "quiet": True,
    'cookiefile':cookies_location,
    'concurrent_fragment_downloads': 256,
    "cachedir": "./cache",

    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320'
        },
        {
            'key': 'FFmpegMetadata',
            'add_metadata': {
                'album': '%(uploader)s', 
                'genre': 'YouTube - %(upload_date)s', 
            }
        },
    ],
}

audio_fallback_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': ffmpeg_location,
    'ffprobe_location':ffprobe_location,
    'no_mtime': True,
    'nocache': False,
    'cookiefile':cookies_location,
    'concurrent_fragment_downloads': 64,
    "cachedir": "./cache",
    "quiet": True,
    
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        },
        {
            'key': 'FFmpegMetadata',
            'add_metadata': {
                'album': '%(uploader)s', 
                'genre': 'YouTube - %(upload_date)s', 
            }
        },
    ],
}

video_fallback_opts = {
    'format': 'bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best[vcodec^=avc1]/best',
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': ffmpeg_location,
    'ffprobe_location':ffprobe_location,
    'no_mtime': True,
    'nocache': False,
    "cachedir": "./cache",
    "quiet": True,
    'cookiefile':cookies_location,
    'concurrent_fragment_downloads': 64,
    'merge_output_format': 'mp4',
    "embedsubtitles": True,
    
}

search_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': ffmpeg_location,
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
    with yt_dlp.YoutubeDL(search_opts) as searcher: # type: ignore
        results = searcher.extract_info(f"ytsearch{total_search}:{query}", download=False)
        return results['entries'] # type: ignore
    
def download(url, only_audio=True, only_captions=False):
    if only_audio:
        options = audio_opts
    elif only_captions:
        options = subtitles
        options['outtmpl'] = '%(title)s.%(ext)s'
        options['skip_download'] = True
    else:
        options = vid_opts

    captions = input('Do you want to download the subtitle as .srt (if avaliable)? (Y / N): ').strip().lower() == 'y'
    if captions:
        for k, v in subtitles.items():
            options[k] = v

    def dynamic_metadata_hook(d):
        if d['status'] == 'finished':
            artist_name = d.get('uploader', 'Unknown Artist')
            d['postprocessor_args'] = [
                '-metadata', f'artist={artist_name}'
            ]

    options["progress_hooks"] = [loader, dynamic_metadata_hook]
    options["js_runtimes"] = {
        "quickjs": {
            "path": "./assets/qjs.exe"
        },
        "deno": {}
    }
    options['remote_components'] = ['ejs:github']

    try:
        with yt_dlp.YoutubeDL(options) as ydl:  # type: ignore
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            print(f"\n[√] Saved to: {os.path.abspath(file_path)}")
            return file_path

    except Exception as e:
        print(f"[!] Initial download try failed: {e}")
        os.system("pip install yt-dlp --upgrade")
        fallback_options = audio_fallback_opts if only_audio else video_fallback_opts

        if captions:
            for k, v in subtitles.items():
                options[k] = v
        try:
            with yt_dlp.YoutubeDL(fallback_options) as fallback:  # type: ignore
                info = fallback.extract_info(url, download=True)
                file_path = fallback.prepare_filename(info)
                print(f"\n[√] Saved (fallback) to: {os.path.abspath(file_path)}")
                return file_path
        except Exception as e2:
            print(f"[X] Fallback also failed: {e2}")
            print("Skipping this item")
            return None


def main():
    s = time.time()
    search_url = input("Do you have the url of the video? (Y/N) ").lower()
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

    a = input("Download only Audio (A) or Video with audio (V) or just captions (C)?: ").strip().lower()
    while a not in ('a', 'v', 'c'):
        a = input("[!] Invalid choice. Please enter 'A', 'V', or 'C': ").strip().lower()

    file_path = download(url, a=='a', a=='c')
    if file_path:
        if input('would you like to compress the file? (Y / N) ').lower().strip() == 'y':
            if a == 'a':
                out = compress_audio(file_path)
            else:
                out = compress_mp4(file_path)
            
            print(f"\n[O] Compressed to {str(out)}")
        else:
            print(f"\n[O] File saved to {str(file_path)}")

    print(f"\n[.] Total time: {time.time() - s:.2f} seconds")

if __name__ == "__main__":
    main()
