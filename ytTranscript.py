import time
import platform
import subprocess
import pygetwindow as gw
from youtube_transcript_api import YouTubeTranscriptApi
import re
import pyautogui
import pystray
from PIL import Image
import threading
import sys
from tkinter import Tk, Text, Scrollbar, Toplevel, RIGHT, Y, END, BOTH

class TranscriptFetcher:
    def __init__(self):
        self.running = False
        self.thread = None
        self.transcript_cache = ""

    def start_monitoring(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.monitor_youtube_tabs)
            self.thread.daemon = True
            self.thread.start()

    def stop_monitoring(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def extract_video_id(self, url):
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
        return match.group(1) if match else None

    def get_chrome_url(self):
        system = platform.system()
        if system == "Windows":
            try:
                from pywinauto import Application
                app = Application(backend="uia").connect(title_re=".*Chrome.*")
                window = app.top_window()
                address_bar = window.child_window(title="Address and search bar", control_type="Edit")
                url = address_bar.get_value()
                return url
            except Exception as e:
                print(f"Windows error: {e}")
                return None
        elif system == "Darwin":  # macOS
            try:
                script = """
                tell application "Google Chrome"
                    set activeTabUrl to URL of active tab of front window
                end tell
                """
                result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
                return result.stdout.strip()
            except Exception as e:
                print(f"macOS error: {e}")
                return None

    def close_youtube_tab(self):
        try:
            if platform.system() == "Windows":
                pyautogui.hotkey('ctrl', 'w')
            elif platform.system() == "Darwin":  # macOS
                pyautogui.hotkey('command', 'w')
        except Exception as e:
            print(f"Error closing tab: {e}")

    def fetch_transcript(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = "\n".join(
                [f"[{entry['start']:.2f}s] {entry['text']}" for entry in transcript]
            )
            self.transcript_cache = transcript_text
            self.close_youtube_tab()
        except Exception as e:
            print(f"Transcript fetch error: {e}")

    def monitor_youtube_tabs(self):
        while self.running:
            try:
                active_window = gw.getActiveWindow()
                if active_window and "YouTube" in active_window.title:
                    url = self.get_chrome_url()
                    if url and "youtube.com/watch" in url:
                        print("YouTube tab detected.")
                        video_id = self.extract_video_id(url)
                        if video_id:
                            print(f"Fetching transcript for Video ID: {video_id}")
                            self.fetch_transcript(video_id)
                time.sleep(5)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)

    def show_transcript(self):
        if not self.transcript_cache:
            self.transcript_cache = "No recent transcript available."
        root = Tk()
        root.title("Transcript Viewer")

        frame = Toplevel(root)
        frame.geometry("600x400")

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        text = Text(frame, wrap='word', yscrollcommand=scrollbar.set)
        text.insert(END, self.transcript_cache)
        text.pack(expand=True, fill=BOTH)

        scrollbar.config(command=text.yview)
        root.mainloop()


def create_icon():
    fetcher = TranscriptFetcher()
    icon_image = Image.new('RGB', (64, 64), color='red')

    def on_start(icon, item):
        fetcher.start_monitoring()
        icon.icon = Image.new('RGB', (64, 64), color='green')

    def on_stop(icon, item):
        fetcher.stop_monitoring()
        icon.icon = Image.new('RGB', (64, 64), color='red')

    def on_show_transcript(icon, item):
        threading.Thread(target=fetcher.show_transcript, daemon=True).start()

    def on_exit(icon, item):
        fetcher.stop_monitoring()
        icon.visible = False
        icon.stop()
        sys.exit()

    menu = pystray.Menu(
        pystray.MenuItem("Start", on_start),
        pystray.MenuItem("Stop", on_stop),
        pystray.MenuItem("Show Transcript", on_show_transcript),
        pystray.MenuItem("Exit", on_exit)
    )

    icon = pystray.Icon("YouTube Transcript Monitor", icon_image, "YouTube Transcript Monitor", menu)
    icon.run()


if __name__ == "__main__":
    create_icon()
