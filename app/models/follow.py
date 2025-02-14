from app.extensions import db
import uuid
from datetime import datetime

class Follow(db.Model):
    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    follower_id = db.Column(db.UUID, db.ForeignKey('user.id'), nullable=False)
    following_id = db.Column(db.UUID, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    follower = db.relationship('User', foreign_keys=[follower_id], backref='following')
    following = db.relationship('User', foreign_keys=[following_id], backref='followers')
