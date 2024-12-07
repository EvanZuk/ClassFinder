from flask_limiter import Limiter
from flask import request

limiter = Limiter(key_func=lambda: request.remote_addr)
