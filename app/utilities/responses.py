from app import app
from flask import jsonify


def error_response(message: str, extra: dict = {}):
    with app.app_context():
        return jsonify({"message": message, "status": "error"} | extra)


def success_response(message: str, extra: dict = {}):
    with app.app_context():
        return jsonify({"message": message, "status": "success"} | extra)
