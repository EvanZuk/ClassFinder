import os
from app import app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db_path = os.environ.get("DB_PATH", "sqlite:///db.sqlite3")
app.config["SQLALCHEMY_DATABASE_URI"] = db_path
db = SQLAlchemy(app)


# if not os.path.exists(db_path):
#     os.makedirs(db_path)
user_class_association = db.Table(
    "user_class",
    db.Model.metadata,
    db.Column(
        "user_id", db.String(20), db.ForeignKey("user.username"), primary_key=True
    ),
    db.Column("class_id", db.String(20), db.ForeignKey("class.id"), primary_key=True),
)


class User(db.Model):
    username = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    classes = db.relationship(
        "Class", secondary=user_class_association, backref="users", lazy=True
    )
    created_at = db.Column(db.DateTime, default=datetime.now)
    created_by = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    tokens = db.relationship("Token", backref="user", lazy=True)

    def __str__(self):
        return self.username
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Class(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(7), nullable=False)
    period = db.Column(db.String(10), nullable=False)
    canvasid = db.Column(db.Integer, nullable=True, default=None)
    lunch = db.Column(db.String(1), nullable=True, default=None)
    created_by = db.Column(db.String(20), nullable=False)
    verified = db.Column(db.Boolean, nullable=False, default=False)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"<Class {self.name} ({self.id})>"

class Token(db.Model):
    token = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    user_id = db.Column(db.String(20), db.ForeignKey("user.username"), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    expire = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now() + timedelta(days=8))

    def __str__(self):
        return self.token + " for " + self.user_id
    
    def __repr__(self):
        return f"<Token {self.token} ({self.user_id})>"


class Schedule(db.Model):
    day = db.Column(db.Date, primary_key=True, nullable=False, unique=True)
    type = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return self.day.strftime("%Y-%m-%d") + " is " + self.type

    def __repr__(self):
        return f"<Schedule {self.day} ({self.type})>"


def db_cleanup():
    """
    Clean up the database by removing everything expired
    """
    expired_tokens = db.session.query(Token).filter(Token.expire < datetime.now())
    expired_schedules = db.session.query(Schedule).filter(Schedule.day < datetime.now().date())

    expired_tokens_count = expired_tokens.delete(synchronize_session=False)
    expired_schedules_count = expired_schedules.delete(synchronize_session=False)

    app.logger.debug(f"Deleted {expired_tokens_count} expired tokens.")
    if expired_schedules_count == 0:
        app.logger.debug(f"Deleted {expired_schedules_count} expired schedules.")
    else:
        app.logger.info(f"Deleted {expired_schedules_count} expired schedules.")
    db.session.commit()

with app.app_context():
    db.create_all()
    db.session.commit()
