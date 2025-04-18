"""
Provides functions to validate user input.
"""

import re
import better_profanity

profanity = better_profanity.Profanity()

def validate_email(email: str):
    """
    Check if an email is valid

    Args:
        email (str): The email to check.
    """
    return re.fullmatch(r"[a-z]*\.[a-z]*[0-9]{0,1}(@s.stemk12.org|@stemk12.org)", email)


def validate_username(username: str):
    """
    Check if a username is valid

    Args:
        username (str): The username
        
    Returns:
        bool: True if the username is valid, False otherwise
    """
    if profanity.contains_profanity(username):
        return False
    if username.lower() in ["admin", "root", "superuser", "moderator", "mod"]:
        return False
    if username.lower().startswith("admin"):
        return False
    return re.fullmatch(r"[a-z0-9_]{3,15}", username)


def validate_room(room: str):
    """
    Check if a room is valid

    Args:
        room (str): The room to check.

    Returns:
        bool: True if the room is valid, False otherwise
    """
    return re.fullmatch(r"(E?[0-9]{3}B?)|MS Cafe|PTECH", room)
