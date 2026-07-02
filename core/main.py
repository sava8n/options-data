"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from log_config import setup_logging
from routes import router

setup_logging()

server = FastAPI(
    title="Options Data API",
    version="1.0.0",
    description="REST analytics for BTC options (from Deribit).",
)

server.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server.include_router(router, prefix="/api")
