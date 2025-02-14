from app.extensions import db
import uuid
from datetime import datetime

class Comment(db.Model):
    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID, db.ForeignKey('user.id'), nullable=False)
    thread_id = db.Column(db.UUID, db.ForeignKey('thread.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='comments')
    thread = db.relationship('Thread', backref='comments')
