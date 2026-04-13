from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.errors import register_exception_handlers
from api.runs import router as runs_router
from api.import_ import router as import_router
from api.normalize import router as normalize_router
from api.analyze import router as analyze_router
from api.recommendations import router as recommendations_router
from api.approvals import router as approvals_router
from api.exports import router as exports_router

app = FastAPI(
    title="Quality Evaluation Analysis Backend",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom exception handlers
register_exception_handlers(app)

# Include all route modules
app.include_router(runs_router)
app.include_router(import_router)
app.include_router(normalize_router)
app.include_router(analyze_router)
app.include_router(recommendations_router)
app.include_router(approvals_router)
app.include_router(exports_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
