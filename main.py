import base64
import datetime
import io
import os

from flask import Flask, render_template, request
from gtts import gTTS, gTTSError
from gtts.lang import tts_langs

MAX_TEXT_LENGTH = 2000
DEFAULT_LANGUAGE = "en"

# All languages supported by gTTS, sorted by their display name.
LANGUAGES = dict(sorted(tts_langs().items(), key=lambda item: item[1]))

app = Flask(__name__)


def synthesize(text: str, language: str, slow: bool) -> bytes:
    """Generate MP3 audio for the text in memory and return its bytes."""
    buffer = io.BytesIO()
    gTTS(text=text, lang=language, slow=slow).write_to_fp(buffer)
    return buffer.getvalue()


@app.route("/", methods=["GET", "POST"])
def index():
    text = request.form.get("text", "").strip()
    language = request.form.get("language", DEFAULT_LANGUAGE)
    slow = request.form.get("slow") == "on"
    context = {
        "languages": LANGUAGES,
        "max_length": MAX_TEXT_LENGTH,
        "text": text,
        "language": language if language in LANGUAGES else DEFAULT_LANGUAGE,
        "slow": slow,
    }

    if request.method == "GET":
        return render_template("index.html", **context)

    error = None
    if not text:
        error = "Please enter some text."
    elif len(text) > MAX_TEXT_LENGTH:
        error = f"Text is too long ({len(text)} characters, max {MAX_TEXT_LENGTH})."
    elif language not in LANGUAGES:
        error = "Unsupported language."

    if error:
        return render_template("index.html", error=error, **context), 400

    try:
        audio = synthesize(text, language, slow)
    except AssertionError:
        # gTTS raises this when the text has nothing speakable (e.g. only punctuation).
        return render_template("index.html", error="The text contains nothing that can be spoken.", **context), 400
    except gTTSError as exc:
        app.logger.warning("gTTS request failed: %s", exc)
        return render_template(
            "index.html",
            error="Could not reach the text-to-speech service. Check your internet connection and try again.",
            **context,
        ), 502

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return render_template(
        "index.html",
        audio_src="data:audio/mpeg;base64," + base64.b64encode(audio).decode("ascii"),
        audio_filename=f"tts-{language}-{timestamp}.mp3",
        **context,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=os.environ.get("FLASK_DEBUG") == "1")
