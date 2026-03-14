from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import warnings
import sys
from api import router as api_router
import uvicorn

# Suppress warnings
warnings.filterwarnings("ignore", message=".*huggingface_hub.*")

# Note: You may see "Error importing huggingface_hub.hf_api" messages during startup.
# These are harmless warnings from LangChain's optional dependencies and don't affect functionality.

# Ensure numpy is available
try:
    import numpy as np
except ImportError:
    print("Warning: numpy not found. Installing numpy...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy as np

# Load environment variables
load_dotenv()

# Verify Groq API key is loaded
groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    print(f"✓ Groq API key loaded (ends with: ...{groq_key[-8:]})")
else:
    print("⚠ Warning: GROQ_API_KEY not found in environment")

app = FastAPI(
    title="Automated EDA System",
    description="A comprehensive system for automated exploratory data analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="uploads"), name="static")

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Automated EDA System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "automated-eda-api"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000,
        reload=True
    )