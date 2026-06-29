import uuid

from flask_login import UserMixin

from database import db
class User(db.Model, UserMixin):
    id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False, default="user")
