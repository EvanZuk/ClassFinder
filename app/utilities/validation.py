import re

def validate_email(email: str):
    """
    Check if an email is valid
    """
    return re.fullmatch(r'[a-z]*\.[a-z]*(@s.stemk12.org|@stemk12.org)', email)

def validate_username(username: str):
    """
    Check if a username is valid
    """
    return re.fullmatch(r'[a-z0-9_]{3,20}', username)

def validate_room(room: str):
    """
    Check if a room is valid
    """
    return re.fullmatch(r'(E?[0-9]{3})|MS Cafe', room)