"""ASGI entry for Vercel: exposes `app` at repo root (see Vercel FastAPI docs)."""

from app.main import app

__all__ = ["app"]
