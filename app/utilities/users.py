"""
This file contains functions for user management.
"""

from typing import Literal
from datetime import datetime, timedelta
import os
import functools
import base64
from flask_bcrypt import Bcrypt
from flask import request, redirect
from app.db import db, User, Token, Class
from app import app

bcrypt = Bcrypt()

def create_user(
    username: str, email: str, password: str, created_by="system", role="user"
):
    """
    Create a user

    Args:
        username (str): The username of the user.
        email (str): The email of the user.
        password (str): The password of the user.
        created_by (str): The user who created the user.
        role (str): The role of the user.

    Returns:
        User: The user that was created.
    """
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(
        username=username,
        email=email,
        password=hashed_password,
        created_by=created_by,
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user

def change_password(user: User, password: str):
    """
    Change a user's password

    Args:
        user (User): The user to change the password for.
        password (str): The new password.

    Returns:
        User: The user with the new password.
    """
    user.password = bcrypt.generate_password_hash(password).decode("utf-8")
    db.session.commit()
    return user

def check_password(username: str, password: str):
    """
    Check if a password is valid for a user

    Args:
        username (str): The username of the user.
        password (str): The password to check.

    Returns:
        bool: Whether the password is valid.
    """
    user = User.query.filter_by(username=username).first()
    if app.config.get("TESTING"):
        app.logger.debug("Testing mode enabled, printing password: '" + password + "'")
    if user and bcrypt.check_password_hash(user.password, password):
        return True
    return False

def create_token(username: str, tokentype: Literal["api", "refresh", "system", "app", "admin"], expiry: datetime = None, scopes: list = None):
    """
    Create a token for a user

    Args:
        username (str): The username of the user.
        tokentype (Literal["api", "refresh", "system", "app", "admin"]): The type of token to create.
        expiry (datetime): The expiry date of the token.

    Returns:
        Token: The token that was created
    """
    nexpiry = expiry
    if nexpiry is None:
        nexpiry = datetime.now()
        if tokentype == "api" or tokentype == "app":
            nexpiry += timedelta(days=60)
        elif tokentype == "refresh":
            nexpiry += timedelta(days=7)
        elif tokentype == "system":
            nexpiry += timedelta(days=30)
        elif tokentype == "admin":
            nexpiry += timedelta(hours=1)
        else:
            nexpiry += timedelta(days=1)
    token = Token(token=os.urandom(30).hex(), user_id=username, type=tokentype, expire=expiry, scopes=" ".join(scopes) if scopes else None)
    db.session.add(token)
    db.session.commit()
    return token

def check_token(token: str):
    """
    Check if a token is valid

    Args:
        token (str): The token string to check.

    Returns:
        User: The user that the token belongs to.
    """
    token = Token.query.filter_by(token=token).first()
    if token:
        user = User.query.filter_by(username=token.user_id).first()
        return user
    return None

def get_token(token: str):
    """
    Get a token

    Args:
        token (str): The token string to get.

    Returns:
        Token: The token.
    """
    return Token.query.filter_by(token=token).first()

def delete_token(token: Token):
    """
    Delete a token

    Args:
        token (Token): The token to delete.

    Returns:
        None
    """
    db.session.delete(token)
    db.session.commit()
    return None

def check_email(email: str):
    """
    Check if an email has a user

    Args:
        email (str): The email to check.

    Returns:
        User: The user with the email.
    """
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    return False

def get_user_count(blacklist_roles: list = []): # pylint: disable=dangerous-default-value
    """
    Get the number of users in the database

    Args:
        blacklist_roles (list): Roles to exclude from the count.

    Returns:
        int: The number of users.
    """
    return User.query.filter(User.role.notin_(blacklist_roles)).count()

def get_user(username: str):
    """
    Get a user by username

    Args:
        username (str): The username of the user.

    Returns:
        User: The user.
    """
    return User.query.filter_by(username=username).first()

def change_user_role(user: User, role: str):
    """
    Change a user's role

    Args:
        user (User): The user to change the role for.
        role (str): The new role.

    Returns:
        User: The user with the new role.
    """
    user.role = role
    db.session.commit()
    return user

def change_username(user: User, username: str, require_change: bool = None):
    """
    Change a user's username

    Args:
        user (User): The user to change the username for.
        username (str): The new username.

    Returns:
        User: The user with the new username.
    """
    if User.query.filter_by(username=username).first():
        raise ValueError("Username already exists")
    old_username = user.username

    # Update related records in other tables
    related_tokens = Token.query.filter_by(user_id=old_username).all()
    related_classes = Class.query.filter(Class.users.any(username=old_username)).all()
    for course in related_classes:
        course.users.remove(user)
    for token in related_tokens:
        token.user_id = username

    # Update created_by for each class
    created_courses = Class.query.filter_by(created_by=old_username).all()
    for course in created_courses:
        course.created_by = username

    # Update username
    user.username = username

    # Update classes
    for course in related_classes:
        course.users.append(user)

    # Update requires_username_change
    if require_change is True:
        user.requires_username_change = True
    elif require_change is False:
        user.requires_username_change = False

    # Commit
    db.session.commit()

    return user

def get_user_by_email(email: str):
    """
    Get a user by email

    Args:
        email (str): The email of the user.

    Returns:
        User: The user.
    """
    return User.query.filter_by(email=email).first()

def delete_user(user: User):
    """
    Delete a user

    Args:
        user (User): The user to delete.

    Returns:
        None
    """
    for token in user.tokens:
        delete_token(token)
    db.session.delete(user)
    db.session.commit()
    return None

def verify_user( # pylint: disable=dangerous-default-value
    func=None,
    required: bool = True,
    allowed_roles: list = ["user", "teacher", "admin", "testing"],
    onfail=lambda: redirect("/login"),
):
    """
    Decorator to verify a user

    Args:
        func: The function to decorate.
        required (bool): Whether the user is required.
        allowed_roles (list): Roles that are allowed.
        onfail: The function to call if the user is not verified.

    This populates the request object with the user and token.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request.user = None
            request.token = None
            auth = request.headers.get("Authorization")
            token = request.cookies.get("token")
            if auth:
                if auth.startswith("Bearer "):
                    app.logger.debug("Trying bearer authentication for " + func.__name__)
                    token = auth.split(" ")[1]
                elif auth.startswith("Basic "):
                    auth = base64.b64decode(auth.split(" ")[1]).decode("utf-8")
                    username, password = auth.split(":")
                    app.logger.debug("Trying basic authentication for " + func.__name__ + " with " + username)
                    if app.config.get("TESTING"):
                        app.logger.debug("Testing mode enabled, printing password (basic): '" + password + "'")
                    if check_password(username, password):
                        user = User.query.filter_by(username=username).first()
                        if user and user.role in allowed_roles:
                            app.logger.debug(
                                "Accepted user "
                                + user.username
                                + " with role "
                                + user.role
                                + " for "
                                + func.__name__
                                + " with basic authentication"
                            )
                            request.user = user
                            return func(*args, **kwargs)
                else:
                    if auth != "":
                        app.logger.debug("Trying legacy authentication for " + func.__name__)
                        token = auth.split(" ")[1]
            if token:
                app.logger.debug("Trying token/refresh authentication for " + func.__name__)
                if app.config.get("TESTING"):
                    app.logger.debug("Testing mode enabled, printing token: '" + token + "'")
                    app.logger.debug("Testing mode enabled, printing header: '" + str(request.headers) + "'")
                user = check_token(token)
                if user and user.role in allowed_roles:
                    token = get_token(token)
                    if token.expire < datetime.now():
                        app.logger.debug("Token for " + user.username + " has expired. Deleting token.")
                        delete_token(token)
                    else:
                        app.logger.debug(
                            "Accepted user "
                            + user.username
                            + " with role "
                            + user.role
                            + " for "
                            + func.__name__
                            + " with token/refresh authentication"
                        )
                        request.user = user
                        request.token = token
                        return func(*args, **kwargs)
            app.logger.debug("Rejected user for " + func.__name__)
            if not required:
                return func(*args, **kwargs)
            failresponse = onfail()
            if request.cookies.get("token"):
                app.logger.debug("Clearing token")
                failresponse.set_cookie(
                    "token",
                    "",
                    httponly=True,
                    samesite="Lax",
                    secure=True,
                    max_age=0,
                )
            if request.cookies.get("admin_token"):
                app.logger.debug("Restoring to admin token")
                failresponse.set_cookie(
                    "token",
                    request.cookies.get("admin_token"),
                    httponly=True,
                    samesite="Lax",
                    secure=True,
                    max_age=604800,
                )
                failresponse.set_cookie(
                    "admin_token",
                    "",
                    httponly=True,
                    samesite="Lax",
                    secure=True,
                    max_age=0,
                )
                return failresponse
            return failresponse

        return wrapper

    return decorator if func is None else decorator(func)
