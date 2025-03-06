"""
Implements rate limiting.
"""
from flask_limiter import Limiter
from flask import request
from app import app

limiter = Limiter(
	app=app,
	key_func=lambda: request.remote_addr,
	storage_uri="memory://",
    default_limits=["100 per minute", "2 per second"] if not app.config.get("TESTING") else ["1000 per second"]
)
