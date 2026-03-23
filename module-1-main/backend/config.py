import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Flask & Extensions Configuration"""
    
    # Core Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-12345")
    DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"

    # Database
    # Fallback to SQLite if DATABASE_URL is not provided
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///datavault.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Security
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-98765")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # API Keys
    NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")

    # File uploads
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploaded_datasets")
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200 MB limit
