from configs import *
from youtube_downloader import Downloader

if __name__ == '__main__':
    d = Downloader(ffmpeg_path=ffmpeg_location, ffprobe_path=ffprobe_location, youtube_cookies_path=yt_cookies_location, 
                   soundcloud_cookies_path=sc_cookies_location, QuickJS_runtime_path=JS_runtime_path)
    if input("Do you have the url of the video / audio (Y / N): ").lower().strip() == 'y':
        url = input("Please provide the URL of the media: ")
        if "youtube.com" in url or "youtu.be" in url or url.startswith(("youtube.com", "youtu.be")):

            a = input("Download only Audio (A) or Video with audio (V) or just captions (C)?: ").strip().lower()
            c = True # assume yes, because this aint open source and i like subtitles
            while a not in ('a', 'v', 'c'):
                a = input("[!] Invalid choice. Please enter 'A', 'V', or 'C': ").strip().lower()
                
            if a !='c':
                c = input("Do you want to download the captions too (if avaliable)? (Y / N): ").lower().strip() == 'y'

            d.download(url,  a=='a', a == 'c', c, True)
        elif url.startswith('https://soundcloud') or url.startswith('soundcloud'):
            d.download(url, True, False, False, True)
        else:
            print('Invalid URL.')
    else:
        d.change_platform(input("Please provide a platform to search (soundcloud / youtube): ").strip().lower())
        results = d.search(input("Enter search query: ") or "Cats")
        
        if d.platform in ('yt', 'youtube'):
            for idx, vid in enumerate(results):
                if 'duration' in vid.keys():
                    print(f"{idx}. {vid['title']} (- {vid['channel']}) [{vid['duration']}s]")
                else:
                    print(f"{idx}. {vid['title']} (- {vid['channel']})")
            
            choice = int(input("Enter choice: "))
            vid_id = results[choice]["id"]
            url = f"https://www.youtube.com/watch?v={vid_id}"
            a = input("Download only Audio (A) or Video with audio (V) or just captions (C)?: ").strip().lower()
            while a not in ('a', 'v', 'c'):
                a = input("[!] Invalid choice. Please enter 'A', 'V', or 'C': ").strip().lower()
                c = False
                if a !='c':
                    c = input("Do you want to download the captions too (if avaliable)? (Y / N): ").lower().strip() == 'y'

            d.download(url,  a=='a', a == 'c', c)
        else:
            for idx, vid in enumerate(results):
                if 'duration' in vid.keys():
                    print(f"{idx}. {vid['title']} (- {vid['uploader']}) [{vid['duration']}s]")
                else:
                    print(f"{idx}. {vid['title']} (- {vid['uploader']})")
            
            choice = int(input("Enter choice: "))
            url = results[choice]['url']
            d.download(url, True, False, False)
