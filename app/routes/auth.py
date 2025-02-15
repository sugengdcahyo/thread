import re
from sqlite3 import IntegrityError

from flask_restx import Namespace, Resource, fields
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.extensions import db
from flask_jwt_extended import create_access_token

auth_ns = Namespace("auth", description="Authentication related operations")

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

# Request Model
user_regis_model = auth_ns.model("UserRegistration", {
    "username": fields.String(required=True, description="Username of the user"),
    "email": fields.String(
        required=True,
        description="User email",
        pattern=EMAIL_REGEX
    ),
    "password": fields.String(required=True, write_only=True, description="User password")
})

user_login_model = auth_ns.model("UserLogin", model={
    "username": fields.String(required=True, description="User email"),
    "password": fields.String(required=True, write_only=True, description="User password")
})

user_model = auth_ns.model("UserResponse", {
    "id": fields.String(description="User ID"),
    "username": fields.String(description="Username"),
    "email": fields.String(description="Email"),
    "is_active": fields.Boolean(description="User active status")
})

token_model = auth_ns.model("AuthResponse", {
    "access_token": fields.String(description="JWT Token"),
    "user": fields.Nested(user_model, description="Logged-in username")
})


class RegisterUser(Resource):
    @auth_ns.expect(user_regis_model)
    # @auth_ns.marshal_with(token_model, envelope="data")
    @auth_ns.response(201, "User registered successfully")
    @auth_ns.response(400, "Bad Request")
    @auth_ns.response(500, "Internal Server Error")
    def post(self):
        """Register a new user and return JWT token"""
        data = request.get_json()

        # 🔥 Validasi email format
        if not re.match(EMAIL_REGEX, data["email"]):
            return {"message": "Invalid email format"}, 400

        email = data["email"].strip().lower()
        username = data["username"].strip().lower()

        # 🔥 Periksa apakah username atau email sudah terdaftar
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return {"message": "Username or email already exists"}, 400

        try:
            # Hash password sebelum disimpan
            hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256")

            # Buat user baru dengan username & email dalam format lowercase
            new_user = User(username=username, email=email, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            # Buat JWT Token setelah user berhasil didaftarkan
            access_token = create_access_token(identity=new_user.id)

            # Return dalam format yang diinginkan
            return auth_ns.marshal({
                "access_token": access_token,
                "user": new_user
            }, token_model), 201

        except IntegrityError:
            db.session.rollback()
            return {"message": "Username or email already exists"}, 400

        except Exception as e:
            db.session.rollback()
            return {"message": f"Unexpected error: {str(e)}"}, 500


class LoginUser(Resource):
    @auth_ns.expect(user_login_model, validate=True)
    @auth_ns.response(401, "Invalid credentials")
    @auth_ns.marshal_with(token_model, envelope="data")
    def post(self):
        """Login a user and return a JWT token"""
        data = request.get_json()

        # Cari user berdasarkan email atau username
        user = User.query.filter(
            (User.email == data["username"]) | (User.username == data["username"])
        ).first()

        if user and check_password_hash(user.password_hash, data["password"]):
            # Buat token JWT
            access_token = create_access_token(identity=user.id)
            return {
                "access_token": access_token,
                "user": user
            }, 200

        # Jika gagal, langsung return tanpa `marshal_with`
        return {"message": "Invalid credentials"}, 401


# Register routes
auth_ns.add_resource(RegisterUser, "/register")
auth_ns.add_resource(LoginUser, "/login")
