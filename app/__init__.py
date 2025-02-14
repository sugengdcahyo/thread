from app.extensions import db, migrate, jwt, cors
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_restx import Api
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize extensions
# db = SQLAlchemy()
# migrate = Migrate()
# jwt = JWTManager()
# cors = CORS()


def create_app():
    app = Flask(__name__)

    # Load credentials from .env
    DB_USER = os.getenv('DB_USER', 'user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'threadapp')

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'supersecretkey')
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['RESTX_MASK_SWAGGER'] = False  # Disable Swagger mask warning

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})

    # Setup Flask-RESTx API
    api = Api(app, version="1.0", title="Thread API", description="API for Thread-like Application")

    # Import models to register them
    with app.app_context():
        from app.models import user, thread, comment, like, follow, notification
        db.create_all()

    # Import blueprints (routes)
    from app.routes.auth import auth_ns
    # from app.routes.thread import thread_ns
    # from app.routes.comment import comment_ns
    # from app.routes.like import like_ns
    # from app.routes.follow import follow_ns
    # from app.routes.notification import notification_ns

    # Register namespaces
    api.add_namespace(auth_ns, path="/auth")
    # api.add_namespace(thread_ns, path="/threads")
    # api.add_namespace(comment_ns, path="/comments")
    # api.add_namespace(like_ns, path="/likes")
    # api.add_namespace(follow_ns, path="/follows")
    # api.add_namespace(notification_ns, path="/notifications")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
