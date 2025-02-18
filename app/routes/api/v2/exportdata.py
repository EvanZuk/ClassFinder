from app import app
from app.utilities.users import verify_user
from app.utilities.responses import error_response
from flask import request

@app.route('/api/v2/user/data')
@verify_user(onfail=lambda:(error_response("You must be logged in to do that."), 401))
def export_data():
    user = request.user
    return {
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "classes": [
            {
                "id": c.id,
                "name": c.name,
                "room": c.room,
                "period": c.period,
                "lunch": c.lunch,
                "verified": c.verified,
                "created_by": c.created_by if c.created_by == user.username else None,
            }
            for c in user.classes
        ],
        "created_at": int(user.created_at.timestamp()),
        "created_by": user.created_by
    }

@app.route('/api/v2/user/tokens')
@verify_user(onfail=lambda:(error_response("You must be logged in to do that."), 401))
def export_tokens():
    user = request.user
    return {
        "tokens": [
            {
                "token": t.token.replace(t.token[:10], "*" * 10),
                "type": t.type,
                "expire": int(t.expire.timestamp())
            }
            for t in user.tokens
        ]
    }