# app/main.py

from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
from dotenv import load_dotenv

from app.routers import chatbot_router
from app.services import db_analysis_service
from app.state import USER_SESSIONS

load_dotenv()

app = FastAPI(title="Nuralance - AI Accounting Assistant")

# --- Setup Directories ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "..", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "templates")
CSV_UPLOADS_DIR = os.path.join(BASE_DIR, "csv_uploads")
DB_STORAGE_DIR = os.path.join(BASE_DIR, "db_storage")
os.makedirs(CSV_UPLOADS_DIR, exist_ok=True)
os.makedirs(DB_STORAGE_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", response_class=HTMLResponse)
async def serve_chat_ui(request: Request):
    """Serves the main chat interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload-csv", response_class=JSONResponse)
async def upload_and_process_csv(session_id: str = Form(...), csv_file: UploadFile = File(...)):
    """
    Handles CSV upload, saves it, converts to SQLite, analyzes the schema,
    and prepares the session for chat.
    """
    if not csv_file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV file.")
    
    csv_path = os.path.join(CSV_UPLOADS_DIR, f"{session_id}.csv")
    db_path = os.path.join(DB_STORAGE_DIR, f"{session_id}.db")
    
    try:
        # Save the uploaded CSV
        with open(csv_path, "wb") as buffer:
            shutil.copyfileobj(csv_file.file, buffer)
        
        # Load CSV data into a new SQLite database
        db_analysis_service.load_csv_to_sqlite(csv_path, db_path)
        
        # Analyze the new database to generate the system prompt
        system_prompt = db_analysis_service.generate_system_prompt(db_path)

    except Exception as e:
        # Clean up files on error
        if os.path.exists(csv_path): os.remove(csv_path)
        if os.path.exists(db_path): os.remove(db_path)
        raise HTTPException(status_code=500, detail=f"Failed to process CSV file: {e}")

    # Store session info in our state manager
    USER_SESSIONS[session_id] = {
        "db_path": db_path,
        "system_prompt": system_prompt
    }
    
    print(f"INFO: Session '{session_id}' initialized successfully.")

    # Extract a short description for the user
    try:
        # A more robust way to get a preview of the prompt's analysis
        analysis_part = system_prompt.split("Your task is to answer user questions")[0]
        short_description = "\n".join(analysis_part.split('\n')[1:]).strip() # Skip first line
    except:
        short_description = "Database was analyzed."

    return {
        "session_id": session_id,
        "message": "CSV file processed successfully! Your data is ready.",
        "db_description": short_description,
    }

app.include_router(chatbot_router.router, prefix="/chatbot", tags=["chatbot"])

@app.get("/health")
async def health_check():
    return {"status": "Nuralance Operational"}