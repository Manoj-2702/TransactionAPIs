from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .utils.utils import read_markdown_file
from server.routes.transaction import router as TransactionRouter


readme_content = read_markdown_file("README.md")

app = FastAPI(
    title="Flagright Task",
    description=(lambda: readme_content if isinstance(readme_content, str) else "")(),
    version="1.0.0",
)

app.include_router(TransactionRouter,tags=["Transactions"])


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
