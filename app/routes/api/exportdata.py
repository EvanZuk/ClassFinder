from app import app
from app.utilities.users import verify_user

@app.route('/api/v2/user/data')
@verify_user
def export_data(user):
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