from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .utils.utils import read_markdown_file
from server.routes.transaction import router as TransactionRouter
import logging

readme_content = read_markdown_file("README.md")

app = FastAPI(
    title="Flagright Task",
    description=(lambda: readme_content if isinstance(readme_content, str) else "")(),
    version="1.0.0",
)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(TransactionRouter,tags=["Transactions"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Custom exception handler for HTTP exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Custom exception handler for generic exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )
