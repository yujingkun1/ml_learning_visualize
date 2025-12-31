import logging
from flask import Blueprint, request, jsonify
import datetime
from functools import wraps

from models import db, User, UserKnowledge, SystemLog

import base64
from io import BytesIO
from PIL import Image

try:
    import imghdr
except Exception:
    imghdr = None
try:
    import requests
except Exception:
    requests = None
import hmac
import hashlib
import json

SECRET_KEY = "your-secret-key-change-in-production"  # 应该从环境变量读取
auth_bp = Blueprint("auth", __name__)


def _b64url_encode(data: bytes) -> str:
    s = base64.urlsafe_b64encode(data).decode("utf-8")
    return s.rstrip("=")


def jwt_encode(payload: dict, secret: str = SECRET_KEY) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b = _b64url_encode(
        json.dumps(payload, separators=(",", ":")).encode("utf-8")
    )
    signing_input = f"{header_b}.{payload_b}".encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b = _b64url_encode(sig)
    return f"{header_b}.{payload_b}.{sig_b}"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            token = token.split(" ")[1]  # Bearer token
            # Manual JWT decode + verify HS256 to avoid dependency
            # differences across environments
            try:
                import base64
                import hmac
                import hashlib
                import json
                import time

                def b64url_decode(input_str: str) -> bytes:
                    rem = len(input_str) % 4
                    if rem > 0:
                        input_str += "=" * (4 - rem)
                    return base64.urlsafe_b64decode(input_str.encode("utf-8"))

                parts = token.split(".")
                if len(parts) != 3:
                    raise ValueError("Invalid token structure")
                header_b, payload_b, sig_b = parts
                signing_input = (header_b + "." + payload_b).encode("utf-8")
                signature = b64url_decode(sig_b)
                expected_sig = hmac.new(
                    SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256
                ).digest()
                if not hmac.compare_digest(signature, expected_sig):
                    raise ValueError("Signature mismatch")
                payload_json = b64url_decode(payload_b).decode("utf-8")
                data = json.loads(payload_json)
                # check exp
                if "exp" in data:
                    if int(data["exp"]) < int(time.time()):
                        raise ValueError("Token expired")
            except Exception as ex:
                logging.warning(
                    f"JWT manual decode failed: {ex}; "
                    f"token header preview: {token[:40]}"
                )
                raise
            current_user_id = data["user_id"]
        except Exception:
            return jsonify({"message": "Token is invalid"}), 401
        return f(current_user_id, *args, **kwargs)

    return decorated


def log_action(user_id, action, resource_type=None, resource_id=None, details=None):
    """记录用户操作日志"""
    try:
        log = SystemLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logging.error(f"Failed to log action: {e}")


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not all([username, email, password]):
            return jsonify({"message": "Missing required fields"}), 400

        # password policy: min 8, must contain lower, upper, digit and special char
        import re

        if (
            len(password) < 8
            or not re.search(r"[a-z]", password)
            or not re.search(r"[A-Z]", password)
            or not re.search(r"\d", password)
            or not re.search(r"[^A-Za-z0-9]", password)
        ):
            return (
                jsonify(
                    {
                        "message": (
                            "Password must be at least 8 characters and include "
                            "uppercase, lowercase, number and symbol"
                        )
                    }
                ),
                400,
            )

        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already exists"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists"}), 400

        user = User(username=username, email=email)
        user.set_password(password)

        # generate default avatar SVG (data URL) using first letter
        # if no avatar provided
        try:
            first = (username or "")[0].upper() if username else "U"
            svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128">
  <rect width="100%" height="100%" fill="#E6E1D8"/>
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
        font-family="Inter, system-ui, sans-serif" font-size="64"
        fill="#1f2937">{first}</text>
</svg>"""
            data_url = "data:image/svg+xml;utf8," + svg
            user.avatar = data_url
        except Exception:
            user.avatar = None

        db.session.add(user)
        db.session.commit()

        # 记录注册日志
        log_action(user.id, "register")

        # 生成JWT token
        token = jwt_encode(
            {
                "user_id": user.id,
                "exp": int(
                    (
                        datetime.datetime.utcnow() + datetime.timedelta(days=7)
                    ).timestamp()
                ),
            }
        )

        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "user": user.to_dict(),
                    "token": token,
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logging.error(f"Registration error: {e}")
        return jsonify({"message": "Registration failed"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        logging.info(f"Login attempt for username: {username}")

        if not all([username, password]):
            logging.warning("Missing credentials")
            return jsonify({"message": "Missing credentials"}), 400

        user = User.query.filter_by(username=username).first()
        if not user:
            logging.warning(f"User not found: {username}")
            return jsonify({"message": "Username not found"}), 401

        logging.info(f"User found: {username} (ID: {user.id})")

        password_check = user.check_password(password)
        logging.info(f"Password check result: {password_check}")

        if not password_check:
            logging.warning(f"Invalid password for user: {username}")
            return jsonify({"message": "Invalid password"}), 401

        # 获取用户知识记录
        knowledge_records = UserKnowledge.query.filter_by(user_id=user.id).all()
        knowledge = [record.to_dict() for record in knowledge_records]

        # 记录登录日志
        log_action(user.id, "login")

        # 生成JWT token
        token = jwt_encode(
            {
                "user_id": user.id,
                "exp": int(
                    (
                        datetime.datetime.utcnow() + datetime.timedelta(days=7)
                    ).timestamp()
                ),
            }
        )

        return (
            jsonify(
                {
                    "message": "Login successful",
                    "user": user.to_dict(),
                    "knowledge": knowledge,
                    "token": token,
                }
            ),
            200,
        )

    except Exception as e:
        logging.exception(f"Login error: {e}")
        # Return detail in development to help debugging
        return jsonify({"message": "Login failed", "detail": str(e)}), 500


@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout(current_user_id):
    try:
        log_action(current_user_id, "logout")
        return jsonify({"message": "Logout successful"}), 200
    except Exception as e:
        logging.error(f"Logout error: {e}")
        return jsonify({"message": "Logout failed"}), 500


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        knowledge_records = UserKnowledge.query.filter_by(user_id=user.id).all()
        knowledge = [record.to_dict() for record in knowledge_records]

        return jsonify({"user": user.to_dict(), "knowledge": knowledge}), 200

    except Exception as e:
        logging.error(f"Get current user error: {e}")
        return jsonify({"message": "Failed to get user info"}), 500


@auth_bp.route("/avatar", methods=["PUT", "POST"])
@token_required
def upload_avatar(current_user_id):
    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        # accept multipart form file (avatar or file) or JSON base64 in body
        file = request.files.get("avatar") or request.files.get("file")
        if file:
            data = file.read()
            # size limit 2MB
            max_size = 2 * 1024 * 1024
            if len(data) > max_size:
                return jsonify({"message": "Avatar exceeds maximum size of 2MB"}), 400
            # detect image type
            try:
                import imghdr

                kind = imghdr.what(None, h=data)
            except Exception:
                kind = None
            if not kind:
                # fallback to PIL
                try:
                    img = Image.open(BytesIO(data))
                    kind = (img.format or "").lower()
                except Exception:
                    return (
                        jsonify({"message": "Uploaded file is not a valid image"}),
                        400,
                    )
            ext = kind or "png"
            data_url = f"data:image/{ext};base64," + base64.b64encode(data).decode(
                "utf-8"
            )
            user.avatar = data_url
        else:
            body = request.get_json(silent=True) or {}
            avatar_data = body.get("avatar")
            if (
                avatar_data
                and isinstance(avatar_data, str)
                and avatar_data.startswith("data:")
            ):
                # optional size check: estimate base64 size
                try:
                    header, b64 = avatar_data.split(",", 1)
                    size_bytes = (len(b64) * 3) // 4
                    if size_bytes > 2 * 1024 * 1024:
                        return (
                            jsonify({"message": "Avatar exceeds maximum size of 2MB"}),
                            400,
                        )
                except Exception:
                    pass
                user.avatar = avatar_data
            else:
                return jsonify({"message": "No avatar provided"}), 400

        db.session.commit()
        log_action(user.id, "upload_avatar")
        return jsonify({"message": "Avatar updated", "user": user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Upload avatar error: {e}")
        return jsonify({"message": "Failed to upload avatar", "detail": str(e)}), 500
