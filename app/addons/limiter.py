from flask_limiter import Limiter
from flask import request
from app import app

limiter = Limiter(app=app, key_func=lambda: request.remote_addr)
