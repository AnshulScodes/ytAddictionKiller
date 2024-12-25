import time
import pygetwindow as gw
from pywinauto import Application
from youtube_transcript_api import YouTubeTranscriptApi
import re
import pyautogui
import pystray
from PIL import Image
import threading
import sys
import tkinter as tk
from tkinter import scrolledtext

class TranscriptFetcher:
    def __init__(self):
        self.running = False
        self.thread = None
        self.recent_transcript = ""

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
        try:
            app = Application(backend="uia").connect(title_re=".*Chrome.*")
            window = app.top_window()
            address_bar = window.child_window(title="Address and search bar", control_type="Edit")
            url = address_bar.get_value()
            return url
        except Exception as e:
            return None

    def close_youtube_tab(self):
        try:
            pyautogui.hotkey('ctrl', 'w')
        except Exception as e:
            print(f"Error closing tab: {e}")

    def fetch_transcript(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = ""
            for entry in transcript:
                transcript_text += f"[{entry['start']:.2f}s] {entry['text']}\n"
            self.recent_transcript = transcript_text
            self.close_youtube_tab()
        except Exception as e:
            self.recent_transcript = f"Transcript fetch error: {e}"

    def monitor_youtube_tabs(self):
        while self.running:  # Run while monitoring is active
            try:
                active_window = gw.getActiveWindow()
                if active_window and "YouTube" in active_window.title:
                    url = self.get_chrome_url()
                    if url and "youtube.com/watch" in url:
                        print("YouTube tab clicked!")
                        video_id = self.extract_video_id(url)
                        if video_id:
                            print(f"Video ID: {video_id}")
                            self.fetch_transcript(video_id)
                time.sleep(5)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)


def create_icon():
    fetcher = TranscriptFetcher()
    icon_image = Image.new('RGB', (64, 64), color='red')

    def on_start(icon, item):
        fetcher.start_monitoring()
        icon.icon = Image.new('RGB', (64, 64), color='green')

    def on_stop(icon, item):
        fetcher.stop_monitoring()
        icon.icon = Image.new('RGB', (64, 64), color='red')

    def on_exit(icon, item):
        fetcher.stop_monitoring()
        icon.visible = False
        icon.stop()
        sys.exit()

    def on_get_recent_transcript(icon, item):
        if fetcher.recent_transcript:
            show_transcript(fetcher.recent_transcript)
        else:
            pyautogui.alert(text="No transcript available.", title='No Transcript', button='OK')

    def show_transcript(transcript):
        # Create the Tkinter window
        root = tk.Tk()
        root.title("YouTube Transcript")

        # Create a scrollable text widget
        text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20)
        text_widget.pack(padx=10, pady=10)

        # Insert the transcript text into the scrollable text widget
        text_widget.insert(tk.END, transcript)
        text_widget.config(state=tk.DISABLED)  # Make the text widget read-only

        # Run the Tkinter event loop
        root.mainloop()

    menu = pystray.Menu(
        pystray.MenuItem("Start", on_start),
        pystray.MenuItem("Stop", on_stop),
        pystray.MenuItem("Get Recent Transcript", on_get_recent_transcript),
        pystray.MenuItem("Exit", on_exit)
    )

    # Create the system tray icon and menu
    icon = pystray.Icon("YouTube Transcript Monitor", icon_image, "YouTube Transcript Monitor", menu)

    # Run the tray icon
    icon.run()


if __name__ == "__main__":
    create_icon()