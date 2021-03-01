from __future__ import unicode_literals
import youtube_dl
import os

url = ""

def urlassign(d):
    global url
    url = d
    download()
    print("Url recieved")


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
    'outtmpl': 'Downloaded/Playnow.mp3'
}
def download():
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        if os.path.exists("Downloaded/Playnow.mp3"):
            os.remove("Downloaded/Playnow.mp3")
        ydl.download([url])
