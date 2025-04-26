import yt_dlp, time

vid_opts = {
    'format': 'bv*[vcodec~="^avc1"]+ba[acodec~="^mp4a"]/bestvideo+bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': './ffmpeg.exe',
    'no_mtime': True,
    'nocache': False,
    'merge_output_format': 'mp4',
    'cookiefile': './youtube.com_cookies.txt',
    'concurrent_fragment_downloads': 64,
}


audio_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': './ffmpeg.exe',
    'no_mtime': True,
    'nocache': False,
    'cookiefile': './youtube.com_cookies.txt',
    'concurrent_fragment_downloads': 64,
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320'
        },
    ],
}

search_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': './ffmpeg.exe',
    'quiet': True,
    'noplaylist': True,
    'nocache': False,
    'extract_flat': True,
}

def search(query, total_search=5):
    print(f"Searching {query}...\n")
    with yt_dlp.YoutubeDL(search_opts) as searcher:
        results = searcher.extract_info(f"ytsearch{total_search}:{query}", download=False)
        return results['entries']

def download(url, only_audio=True):
    options = audio_opts if only_audio else vid_opts
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

s = time.time()
results = search("to be human nightcore // lyrics")

for idx, vid in enumerate(results):
    print(f"{idx}. {vid['title']} (- {vid['channel']})")

print()
choice = int(input("Enter choice: "))
print(f"\nDownloading: {results[choice]['title']} (- {results[choice]['channel']})\n")

video_id = results[choice]["id"]
full_url = f"https://www.youtube.com/watch?v={video_id}"
download(full_url,)

print("\n" + "Done".center(50))
print(f"\nTotal time: {time.time() - s:.2f} seconds")
