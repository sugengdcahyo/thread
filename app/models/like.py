from app.extensions import db
import uuid
from datetime import datetime

class Like(db.Model):
    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID, db.ForeignKey('user.id'), nullable=False)
    thread_id = db.Column(db.UUID, db.ForeignKey('thread.id'), nullable=True)
    comment_id = db.Column(db.UUID, db.ForeignKey('comment.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='likes')
    thread = db.relationship('Thread', backref='likes')
    comment = db.relationship('Comment', backref='likes')
