import time
import pygetwindow as gw
from pywinauto import Application
from youtube_transcript_api import YouTubeTranscriptApi
import re
import pyautogui

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def get_chrome_url():
    try:
        app = Application(backend="uia").connect(title_re=".*Chrome.*")
        window = app.top_window()
        address_bar = window.child_window(title="Address and search bar", control_type="Edit")
        url = address_bar.get_value()
        return url
    except Exception as e:
        return None

def close_youtube_tab():
    try:
        pyautogui.hotkey('ctrl', 'w')
    except Exception as e:
        print(f"Error closing tab: {e}")

def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        for entry in transcript:
            print(f"[{entry['start']:.2f}s] {entry['text']}")
        close_youtube_tab()
    except Exception as e:
        print(f"Transcript fetch error: {e}")

def monitor_youtube_tabs():
    while True:
        try:
            active_window = gw.getActiveWindow()
            if active_window and "YouTube" in active_window.title:
                url = get_chrome_url()
                if url and "youtube.com/watch" in url:
                    print("YouTube tab clicked! THANK YOU SO MUCH FOR USING THIS!!!")
                    video_id = extract_video_id(url)
                    if video_id:
                        print(f"Video ID: {video_id}")
                        fetch_transcript(video_id)
            time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_youtube_tabs()
