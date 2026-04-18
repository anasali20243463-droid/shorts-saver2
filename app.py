from flask import Flask, render_template, request, Response
import yt_dlp
import threading
import json

app = Flask(__name__)

progress_data = {"percent": 0}

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d['_percent_str'].replace('%','').strip()
        try:
            progress_data["percent"] = float(percent)
        except:
            pass

    if d['status'] == 'finished':
        progress_data["percent"] = 100


def download_video(url):

    progress_data["percent"] = 0

    ydl_opts = {
    'format': 'best',
    'outtmpl': '%(title)s.%(ext)s',
    'progress_hooks': [progress_hook],
    'quiet': True,
    'no_warnings': True,
    'extractor_args': {
        'youtube': {
            'skip': ['dash', 'hls']
        }
    }
}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start_download", methods=["POST"])
def start_download():

    url = request.form["url"]

    thread = threading.Thread(target=download_video, args=(url,))
    thread.start()

    return "started"


@app.route("/progress")
def progress():

    def generate():
        while True:
            yield f"data:{json.dumps(progress_data)}\n\n"

    return Response(generate(), mimetype='text/event-stream')


if __name__ == "__main__":
    import os

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
