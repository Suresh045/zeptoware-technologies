# config.py
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))  # default 10 MB

# Priority order for DB connection:
# 1) If DATABASE_URL env var present -> use it (allows Heroku-style URLs)
# 2) Else if DB_USER & DB_NAME present -> build a MySQL URI (pymysql driver) and URL-encode password
# 3) Fallback: local SQLite file
DATABASE_URL = os.getenv("DATABASE_URL")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")

if DATABASE_URL:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
elif DB_USER and DB_NAME:
    # URL-encode the password so special characters (like @) won't break the URI
    DB_PASS_ESC = quote_plus(DB_PASS or "")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASS_ESC}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
else:
    # fallback sqlite (same location as before)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL_SQLITE',
        f"sqlite:///{os.path.join(BASE_DIR, 'resumes_semantic.db')}"
    )

# Flask secret key (override with env var for production)
FLASK_SECRET = os.environ.get('FLASK_SECRET', 'dev_secret_key')

# SentenceTransformer model name (can change to another model)
EMBEDDING_MODEL_NAME = os.environ.get('EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2')
