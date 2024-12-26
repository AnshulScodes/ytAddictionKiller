from yt_dlp import YoutubeDL

def get_youtube_details_yt_dlp(url: str) -> dict:
    try:
        ydl_opts = {
            'extractor_args': {
                'generic': 'impersonate'
            },
            'quiet': True  # Suppress unnecessary output
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info["title"], 
                "creator": info["uploader"],
                "duration_seconds": info["duration"]
            }
    except Exception as e:
        return {"error": str(e)}
