import yt_dlp
import os
import pathlib
import subprocess
from copy import deepcopy

YOUTUBE = ('yt', 'youtube')

class Downloader:
    def __init__(self, ffmpeg_path="ffmpeg", ffprobe_path='ffprobe', download_workers = 256, youtube_cookies_path='youtube_cookies.txt',  soundcloud_cookies_path='soundcloud_cookies.txt', default = 'youtube',
                 subs_langs = ["en.*", 'jp.*'], QuickJS_runtime_path = 'assets/qjs.exe', cache_dir = "./cache", UI_loading_callback = None) -> None:
        self.ffmpeg = ffmpeg_path
        self.ffprobe = ffprobe_path
        self.yt_cookies = youtube_cookies_path
        self.sc_cookies = soundcloud_cookies_path
        self.download_workers = download_workers
        self.UI_loading_callback = UI_loading_callback
        self.cookies_map = {
            'yt':self.yt_cookies,
            'youtube': self.yt_cookies,
            'sc': self.sc_cookies,
            'soundcloud': self.sc_cookies
        }
        self.default = default
        self.platform = self.default.lower()
        self.cache_dir = cache_dir
        self.init(subs_langs=subs_langs, QJS_runtime_path=QuickJS_runtime_path)
    
    def _get_cookies(self, platform):
        platform = "".join(platform.split()).lower()
        cookies = self.cookies_map.get(platform, self.cookies_map.get(self.default))
        return cookies
    
    def _base_options(self):
        return {
            'ffmpeg_location': self.ffmpeg,
            'ffprobe_location': self.ffprobe,
            'no_mtime': True,
            'nocache': False,
            "quiet": True,
            "cachedir": self.cache_dir,
            'cookiefile': self._get_cookies(self.platform),
        }

    def _create_options(self):
        out = '[SC] %(title)s.%(ext)s' if self.platform.lower() in ('sc', 'soundcloud', 'sound cloud') else ('[YT] %(title)s.%(ext)s' if self.platform.lower() in YOUTUBE else'%(title)s.%(ext)s')
        cookies = self._get_cookies(self.platform)
        self.video_options = self._base_options() | {
        'format':'bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best[vcodec^=avc1]/best',
        'outtmpl': out,
        'merge_output_format': 'mp4',
        'concurrent_fragment_downloads': self.download_workers,
        "embedsubtitles": True,
        }

        self.subtitles_options = {
        "writesubtitles": True,
        "subtitleslangs": self.subs_langs,
        "convertsubtitles": "vtt",
        'subtitlesformat': "vtt/srt",
        "embedsubtitles": True,
        }

        self.audio_options = self._base_options() | {
            'format': 'bestaudio/best',
            'outtmpl': out,
            'concurrent_fragment_downloads': self.download_workers,

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
                        'genre': 'YouTube - %(upload_date)s' if self.platform in YOUTUBE else "SoundCloud - %(upload_date)s", 
                    }
                },
            ],
        }

        self.audio_fallback_options = self._base_options() | {
            'format': 'bestaudio/best',
            'outtmpl': out,
            'concurrent_fragment_downloads': self.download_workers // 4,
            
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

        self.video_fallback_options = self._base_options() | {
            'format': 'bestvideo[vcodec^=avc1]+bestaudio[ext=m4a]/best[vcodec^=avc1]/best',
            'outtmpl': out,
            'concurrent_fragment_downloads': self.download_workers // 4,
            'merge_output_format': 'mp4',
            "embedsubtitles": True,
        }

        self.search_options = self._base_options() | {
            'format': 'bestaudio/best',
            'outtmpl': out,
            'extract_flat': True,
            'concurrent_fragment_downloads': self.download_workers,
        }

    def update_dlp(self, pip_reference= "pip"): 
        subprocess.run(f"{pip_reference} install yt-dlp --upgrade".split())

    def init(self, subs_langs = ["en.*", 'jp.*'], QJS_runtime_path = 'qjs.exe'):
        self.subs_langs = subs_langs
        self.QJS_runtime = QJS_runtime_path

        self._create_options()

        if not os.path.exists("./cache"):
            os.mkdir("./cache")
        if not os.path.exists("./assets"):
            os.mkdir("./assets")
            print(f"Please add \n'ffmpeg.exe'\nand\n'{self.sc_cookies}' or / and '{self.yt_cookies}' files to continue")
            raise FileNotFoundError(f"Please add \n'ffmpeg.exe'\nand\n'{self.sc_cookies}' or / and '{self.yt_cookies}' files to continue (you may ignore this warning if you have the FFMPEG and / or FFPROBE and don't want to use cookies.)")
    
    def change_platform(self, platform):
        self.platform = platform
        self._create_options()

    def _detect_platform_from_url(self, url:str):
        if url.startswith('https://soundcloud') or url.startswith('soundcloud') or url.startswith('http://soundcloud') or 'soundcloud' in url:
           self.change_platform("soundcloud")
        elif "youtube.com" in url or "youtu.be" in url or url.startswith(("youtube.com", "youtu.be")):
            self.change_platform("youtube")
        else:
            self.change_platform(self.default)

    def search(self, query, total_search=5):
        print(f"[O] Searching '{query}'...\n")
        with yt_dlp.YoutubeDL(self.search_options) as searcher: # type: ignore
            search_query = f"ytsearch{total_search}:{query}" if self.platform.lower() in YOUTUBE else f"scsearch{total_search}:{query}"
            results = searcher.extract_info(search_query, download=False)
            return results['entries'] # type: ignore

    def download(self, url, only_audio=True, only_captions=False, captions = True, auto_cookies=False):

        if auto_cookies:
            self._detect_platform_from_url(url)

        if only_audio:
            options = self.audio_options
            if only_captions: 
                options = deepcopy(options)
                for k, v in self.subtitles_options.items():
                    options[k] = v 
        elif only_captions:
            options = deepcopy(self.subtitles_options)
            options['outtmpl'] = '%(title)s.%(ext)s'
            options['skip_download'] = True
        else:
            options = self.video_options

        options = deepcopy(options)
        options['cookiefile'] = self._get_cookies(self.platform) # IDC if its repetitive 

        if captions and self.platform in YOUTUBE:
            for k, v in self.subtitles_options.items():
                options[k] = v

        def dynamic_metadata_hook(d):
            if d['status'] == 'finished':
                artist_name = d.get('uploader', 'Unknown Artist')
                d['postprocessor_args'] = [
                    '-metadata', f'artist={artist_name}'
                ]

        options["progress_hooks"] = [dynamic_metadata_hook]
        if self.UI_loading_callback:
            options["progress_hooks"].append(self.UI_loading_callback)

        if os.path.exists(self.QJS_runtime):
            options["js_runtimes"] = {
                "quickjs": {
                    "path": self.QJS_runtime
                },
                "deno": {}
            }
        else:
            print('bruh. ensure JS runtime path is valid')
        
        options['remote_components'] = ['ejs:github']

        try:
            with yt_dlp.YoutubeDL(options) as ydl:  # type: ignore
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                print(f"\n[√] Saved to: {os.path.abspath(file_path)}")
                return file_path

        except Exception as e:
            print(f"[!] Initial download try failed: {e}")
            fallback_options = self.audio_fallback_options if only_audio else self.video_fallback_options
            fallback_options = deepcopy(fallback_options)
            fallback_options['cookiefile'] = self._get_cookies(self.platform) # IDC if its repetitive 
            fallback_options["js_runtimes"] = {
            "quickjs": {
                "path": self.QJS_runtime
            },
            "deno": {}
            }
            fallback_options['remote_components'] = ['ejs:github']

            if captions:
                for k, v in self.subtitles_options.items():
                    fallback_options[k] = v
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

    def compress_audio(self, input_path):
        input_path = pathlib.Path(input_path)
        output_path = input_path.with_name(input_path.stem + "_compressed" + input_path.suffix)
        
        if input_path.suffix.lower() in [".wav", ".flac"]:
            subprocess.run([
                self.ffmpeg,
                "-i", str(input_path),
                "-compression_level", "12",
                str(output_path)
            ], check=True)
        else:
            subprocess.run([
                self.ffmpeg,
                "-i", str(input_path),
                "-b:a", "192k",
                str(output_path)
            ], check=True)
        return output_path

    def compress_mp4(self, input_path):
        output_path = pathlib.Path(input_path).with_name(pathlib.Path(input_path).stem + "_compressed.mp4")
        
        subprocess.run([
        self.ffmpeg,
            "-i", str(input_path),
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "18", 
            "-c:a", "copy",
            str(output_path)
        ], check=True)
        return output_path
