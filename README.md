# TTS — Text to Speech

A small Flask web app that turns text into speech. Type some text, pick one of 60+ languages, and play or download the generated MP3 right in the browser.

Speech is generated with [gTTS](https://github.com/pndurette/gTTS) (Google Text-to-Speech), so an internet connection is required.

## Features

- Every language gTTS supports (the list is read from gTTS at startup, so new languages show up automatically after an upgrade)
- Optional slow speech
- Play in the browser or download as MP3
- Your text, language and speed are kept after each submit
- Clear error messages for empty or overlong text, unsupported languages and network failures
- Nothing is written to disk: audio is generated in memory, so concurrent users never interfere with each other

## Requirements

- Python 3.10 or newer
- Internet access (gTTS calls Google's TTS service)

## Getting started

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the development server
python main.py
```

Then open <http://127.0.0.1:5000>.

To turn on Flask's debug mode (auto-reload and the interactive debugger), set `FLASK_DEBUG=1` before starting:

```bash
# Windows (PowerShell)
$env:FLASK_DEBUG = "1"; python main.py
# macOS / Linux
FLASK_DEBUG=1 python main.py
```

## How it works

1. The form on `/` posts the text, the language code and the "slow" option.
2. `main.py` validates the input (max 2000 characters, see `MAX_TEXT_LENGTH`) and asks gTTS to generate the MP3 into an in-memory buffer.
3. The page is re-rendered with the audio embedded as a `data:` URL, used by both the `<audio>` player and the download link.

## Project structure

```
.
├── main.py            # Flask app: validation, speech generation, the "/" route
├── templates/
│   ├── base.html      # Base layout and global styles
│   └── index.html     # Form, language picker, audio player and download link
├── requirements.txt
└── Procfile           # Process definition for Heroku-style hosting
```

## Deployment

The `Procfile` runs the app with Gunicorn:

```
web: gunicorn main:app
```

This works on Heroku and similar platforms. Gunicorn does not run on Windows; use `python main.py` for local development there.
