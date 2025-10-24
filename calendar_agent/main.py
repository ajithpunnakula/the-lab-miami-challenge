from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import sync, remind, stats, digest
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Calendar Sync & Reminder Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sync.router, prefix="/api")
app.include_router(remind.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(digest.router, prefix="/api")

@app.get("/")
async def root():
    return {
        "service": "Calendar Sync & Reminder Agent",
        "status": "active",
        "data_source": "Luma (live)",
        "endpoints": [
            "/api/sync",
            "/api/remind",
            "/api/updates",
            "/api/digest",
            "/api/stats"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}