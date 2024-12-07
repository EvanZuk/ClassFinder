from flask import jsonify

def error_response(message: str):
    return jsonify({'message': message, "status": "error"})

def success_response(message: str):
    return jsonify({'message': message, "status": "success"})