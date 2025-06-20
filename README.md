
# Aquatune Server 🎧💧
**Requires Python 3.8+**

**Aquatune Server** is the backend engine for Alina’s synchronized swimming music processing project. It allows users to upload music tracks and metadata files that indicate when swimmers are underwater or above water. The server processes the audio using sound design techniques (like underwater muffling and EQ filtering) to simulate how music is perceived by swimmers during a routine.

This is designed to help synchronized swimming teams prepare and practice with a realistic auditory experience that matches live conditions.

---

## 🚀 Features

- 🎵 Upload original audio and routine metadata files
- 🌀 Process music with underwater/above-water transitions
- 📥 Download the processed audio and updated metadata
- ⚡ FastAPI-based HTTP interface with interactive Swagger docs

---
## ⚡ Quickstart

```bash
git clone https://github.com/alinaqzhu/aquatune.git
cd aquatune
pip install -r requirements.txt
uvicorn main:app --reload
```
---

## 🧩 Dependencies

| Package     | Purpose                              |
|-------------|--------------------------------------|
| `fastapi`   | API server framework                 |
| `uvicorn`   | ASGI server for running FastAPI      |
| `pydub`     | Audio manipulation and processing    |
| `ffmpeg`    | Required backend for `pydub`         |
| `python-multipart` | Required for file uploads    |

Install them all with:

```bash
pip install -r requirements.txt
```

---

## 📦 Installation

1. **Clone the repo**

```bash
git clone https://github.com/your-username/aquatune.git
cd aquatune
```

2. **Install Python dependencies**

```bash
pip install fastapi uvicorn pydub python-multipart
```

3. **Install `ffmpeg` (required by pydub)**

Mac:
```bash
brew install ffmpeg
```

Ubuntu:
```bash
sudo apt update
sudo apt install ffmpeg
```

Windows:
- Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Add to your system PATH

---

## 🏁 Running the Server

```bash
uvicorn main:app --reload
```

Visit the interactive API at:  
📍 [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📂 Project Structure

```
aquatune-server/
├── main.py               # FastAPI server
├── uploads/              # Uploaded audio and metadata
├── processed/            # Processed audio and output files
├── static/index.html     # Optional HTML upload UI
├── README.md
```

---

## 🧪 API Endpoints

| Method | Endpoint              | Description                          |
|--------|------------------------|--------------------------------------|
| POST   | `/upload/`             | Upload audio + metadata              |
| POST   | `/process/`            | Process uploaded files               |
| GET    | `/download/audio/{}`   | Download processed audio file        |
| GET    | `/download/meta/{}`    | Download processed metadata file     |

---

## 👩‍💻 Created by Alina  
For swimmers, by a swimmer. 🏊‍♀️🎶
