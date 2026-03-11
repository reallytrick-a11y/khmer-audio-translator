import os
import subprocess
from flask import Flask, render_template, request
from google.genai import Client

API_KEY = "AIzaSyDLASPMkNazsgFIjMdJvJHjEPri9yJIAGg"

client = Client(api_key=API_KEY)
MODEL = "gemini-2.5-flash"

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def convert_mp4_to_mp3(input_file):

    output = input_file.replace(".mp4", ".mp3")

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", input_file,
        output
    ])

    return output


@app.route("/", methods=["GET", "POST"])
def index():

    title = ""
    khmer = ""
    vietnamese = ""

    if request.method == "POST":

        file = request.files["audio"]

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        if filepath.endswith(".mp4"):
            filepath = convert_mp4_to_mp3(filepath)

        audio_file = client.files.upload(file=filepath)

        prompt = """
Nghe audio tiếng Khmer này.

Trả kết quả theo đúng format sau:

TITLE:
Chào bạn, đây là bản phiên âm và bản dịch từ audio bạn cung cấp.

KHMER:
...

VIETNAMESE:
...
"""

        response = client.models.generate_content(
            model=MODEL,
            contents=[audio_file, prompt]
        )

        text = response.text

        try:

            title = text.split("KHMER:")[0].replace("TITLE:", "").strip()

            khmer = text.split("KHMER:")[1].split("VIETNAMESE:")[0].strip()

            vietnamese = text.split("VIETNAMESE:")[1].strip()

        except:
            khmer = text

    return render_template(
        "index.html",
        title=title,
        khmer=khmer,
        vietnamese=vietnamese
    )


if __name__ == "__main__":
    app.run(debug=True)