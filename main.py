import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pytube import YouTube
import threading
import time

class YouTubeDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Video Downloader")
        self.geometry("600x500")
        self.configure(bg='#f0f0f0')

        self.url_label = tk.Label(self, text="Video URL:", bg='#f0f0f0')
        self.url_label.pack(pady=10)

        self.url_entry = tk.Entry(self, width=50)
        self.url_entry.pack(pady=5)

        self.get_info_button = tk.Button(self, text="Get Video Info", command=self.get_video_info)
        self.get_info_button.pack(pady=10)

        self.format_label = tk.Label(self, text="Select Format and Quality:", bg='#f0f0f0')
        self.format_label.pack(pady=10)

        self.format_listbox = tk.Listbox(self, selectmode=tk.SINGLE, width=80, height=10)
        self.format_listbox.pack(pady=10)

        self.download_button = tk.Button(self, text="Download", state=tk.DISABLED, command=self.start_download)
        self.download_button.pack(pady=10)

        self.progress_label = tk.Label(self, text="", bg='#f0f0f0')
        self.progress_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=10)

        self.style = ttk.Style(self)
        self.style.configure('TButton', font=('Helvetica', 12))
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TEntry', font=('Helvetica', 12))

        self.directory = ""
        self.streams_info = []

    def get_video_info(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube video URL")
            return
        
        try:
            self.yt = YouTube(url)
            streams = self.yt.streams.filter(adaptive=True).all() + self.yt.streams.filter(progressive=True).all()
            
            self.format_listbox.delete(0, tk.END)
            self.streams_info = []

            audio_streams = []
            video_streams = []

            for stream in streams:
                if stream.type == "audio":
                    audio_streams.append(stream)
                elif stream.type == "video":
                    video_streams.append(stream)

            audio_streams.sort(key=lambda x: int(x.abr.split('kbps')[0]) if x.abr else 0)
            video_streams.sort(key=lambda x: int(x.resolution[:-1]) if x.resolution else 0)

            for stream in audio_streams:
                info = f"Audio - {stream.abr} - {stream.mime_type} - {round(stream.filesize / (1024 * 1024), 2)} MB"
                self.format_listbox.insert(tk.END, info)
                self.streams_info.append(stream)

            for stream in video_streams:
                info = f"Video - {stream.resolution} - {stream.mime_type} - {round(stream.filesize / (1024 * 1024), 2)} MB"
                self.format_listbox.insert(tk.END, info)
                self.streams_info.append(stream)

            self.download_button.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to get video info: {e}")

    def start_download(self):
        selected_index = self.format_listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select a format and quality")
            return

        self.selected_stream = self.streams_info[selected_index[0]]
        
        self.directory = filedialog.askdirectory()
        if not self.directory:
            messagebox.showerror("Error", "Please select a directory")
            return
        
        self.progress_label.config(text="Downloading...")
        self.progress_bar['value'] = 0

        download_thread = threading.Thread(target=self.download_video)
        download_thread.start()
        self.update_progress()

    def download_video(self):
        try:
            self.start_time = time.time()
            self.selected_stream.download(output_path=self.directory)
            messagebox.showinfo("Success", f"Video downloaded successfully in {self.directory}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download video: {e}")
        finally:
            self.progress_label.config(text="Download Complete")
            self.progress_bar['value'] = 100

    def update_progress(self):
        if self.progress_bar['value'] < 100:
            elapsed_time = time.time() - self.start_time
            downloaded_size = self.selected_stream.filesize * (self.progress_bar['value'] / 100)
            remaining_size = self.selected_stream.filesize - downloaded_size
            estimated_time = (elapsed_time / downloaded_size) * remaining_size if downloaded_size else 0

            self.progress_label.config(
                text=f"Downloaded: {self.progress_bar['value']}% - Elapsed Time: {int(elapsed_time)}s - Estimated Time: {int(estimated_time)}s"
            )

            self.progress_bar['value'] += 1  
            self.after(1000, self.update_progress)  

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
