from sqlalchemy import create_engine, text
from config import SQLALCHEMY_DATABASE_URI

print("Using URI (host+path):", SQLALCHEMY_DATABASE_URI.split('@')[-1])
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False, future=True)
with engine.connect() as conn:
    r = conn.execute(text("SELECT 1"))
    print("DB test result:", r.fetchone())
