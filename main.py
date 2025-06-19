from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
from pydub import AudioSegment
import os
import shutil

app = FastAPI()

UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_files(audio_file: UploadFile = File(...), meta_file: UploadFile = File(...)):
    audio_path = os.path.join(UPLOAD_DIR, audio_file.filename)
    meta_path = os.path.join(UPLOAD_DIR, meta_file.filename)
    
    with open(audio_path, "wb") as f:
        shutil.copyfileobj(audio_file.file, f)

    with open(meta_path, "wb") as f:
        shutil.copyfileobj(meta_file.file, f)
    
    return {"audio": audio_file.filename, "meta": meta_file.filename}


@app.post("/process/")
def process_files(audio_filename: str = Form(...), meta_filename: str = Form(...)):
    input_audio_path = os.path.join(UPLOAD_DIR, audio_filename)
    input_meta_path = os.path.join(UPLOAD_DIR, meta_filename)
    print(input_audio_path)
    print(input_meta_path)

    if not os.path.exists(input_audio_path) or not os.path.exists(input_meta_path):
        return {"error": "File(s) not found"}
    
    # Dummy audio processing: reverse audio
    audio = AudioSegment.from_file(input_audio_path)
    processed_audio = audio.reverse()
    
    processed_audio_path = os.path.join(PROCESSED_DIR, f"processed_{audio_filename}")
    processed_meta_path = os.path.join(PROCESSED_DIR, f"processed_{meta_filename}")

    processed_audio.export(processed_audio_path, format="wav")

    # Dummy metadata processing: append text
    with open(input_meta_path, "r") as f_in, open(processed_meta_path, "w") as f_out:
        content = f_in.read()
        f_out.write(content + "\n[Processed]")

    return {"processed_audio": processed_audio_path, "processed_meta": processed_meta_path}


@app.get("/download/audio/{filename}")
def download_processed_audio(filename: str):
    path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(path):
        return {"error": "File not found"}
    return FileResponse(path, media_type="audio/wav", filename=filename)


@app.get("/download/meta/{filename}")
def download_processed_meta(filename: str):
    path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(path):
        return {"error": "File not found"}
    return FileResponse(path, media_type="text/plain", filename=filename)
