import uuid

from sqlalchemy import UUID
from flask_login import UserMixin
from database import db
class User(db.Model, UserMixin):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
