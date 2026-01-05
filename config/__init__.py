import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

# Database Values
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "")
DB_PORT = int(os.getenv("DB_PORT", 3306))

DB_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# Importing Config Classes
from .default import Default
from .development import Development
from .production import Production

__all__ = ['Default', 'Development', 'Production', 'DB_URL', 'DB_USER', 'DB_PASS', 'DB_HOST', 'DB_NAME', 'DB_PORT']