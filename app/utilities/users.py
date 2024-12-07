from app.db import db, User, Token
from app import app
from flask_bcrypt import Bcrypt
from flask import request, redirect
from typing import Literal
import os
import functools
import base64

bcrypt = Bcrypt()

def create_user(username: str, email: str, password: str, created_by="system", role="user"):
    """
    Create a user
    """
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, email=email, password=hashed_password, created_by=created_by, role=role)
    db.session.add(user)
    db.session.commit()
    return user

def change_password(user: User, password: str):
    """
    Change a user's password
    """
    user.password = bcrypt.generate_password_hash(password).decode('utf-8')
    db.session.commit()
    return user

def check_password(username: str, password: str):
    """
    Check if a password is valid for a user
    """
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return True
    return False

def create_token(username: str, type: Literal["api", "refresh", "system"]="api"):
    """
    Create a token for a user
    type can be either "api", "refresh", or "system"
    """
    token = Token(token=os.urandom(30).hex(), user_id=username, type=type)
    db.session.add(token)
    db.session.commit()
    return token

def check_token(token: str):
    """
    Check if a token is valid
    """
    token = Token.query.filter_by(token=token).first()
    if token:
        user = User.query.filter_by(username=token.user_id).first()
        return user
    return None

def get_token(token: str):
    """
    Get a token
    """
    return Token.query.filter_by(token=token).first()

def delete_token(token: Token):
    """
    Delete a token
    """
    db.session.delete(token)
    db.session.commit()
    return None

def check_email(email: str):
    """
    Check if an email has a user
    """
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    return False

def get_user_count():
    """
    Get the number of users
    """
    return User.query.count()

def get_user(username: str):
    """
    Get a user by username
    """
    return User.query.filter_by(username=username).first()

def get_user_by_email(email: str):
    """
    Get a user by email
    """
    return User.query.filter_by(email=email).first()

def delete_user(user: User):
    """
    Delete a user
    """
    db.session.delete(user)
    db.session.commit()
    return None

def verify_user(func=None, required: bool=True, allowed_roles: list=["user", "teacher", "admin"], onfail=redirect('/login')):
    """
    Decorator to verify a user
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            auth = request.headers.get('Authorization')
            token = request.cookies.get('token')
            
            if auth:
                if auth.startswith('Bearer '):
                    token = auth.split(' ')[1]
                elif auth.startswith('Basic '):
                    auth = base64.b64decode(auth.split(' ')[1]).decode('utf-8')
                username, password = auth.split(':')
                if check_password(username, password):
                    user = User.query.filter_by(username=username).first()
                    if user and user.role in allowed_roles:
                        app.logger.debug('Accepted user ' + user.username + ' with role ' + user.role + ' for ' + func.__name__ + ' with basic authentication')
                        return func(user, *args, **kwargs)
                return onfail
            if token:
                user = check_token(token)
                if user and user.role in allowed_roles:
                    app.logger.debug('Accepted user ' + user.username + ' with role ' + user.role + ' for ' + func.__name__ + ' with token/refresh authentication')
                    return func(user, *args, **kwargs)
            app.logger.debug('Rejected user for ' + func.__name__)
            if not required:
                return func(None, *args, **kwargs)
            failresponse = onfail
            app.logger.debug(request.cookies)
            if request.cookies.get('token'):
                app.logger.debug('Clearing token')
                failresponse.set_cookie('token', '', httponly=True, samesite='Strict', secure=True, max_age=0)
            if request.cookies.get('admin_token'):
                app.logger.debug('Restoring to admin token')
                failresponse.set_cookie('token', request.cookies.get('admin_token'), httponly=True, samesite='Strict', secure=True, max_age=604800)
                failresponse.set_cookie('admin_token', '', httponly=True, samesite='Strict', secure=True, max_age=0)
                return failresponse
            return failresponse
        return wrapper
    return decorator if func is None else decorator(func)