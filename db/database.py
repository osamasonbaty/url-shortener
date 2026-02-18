from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

user = "postgres"
password = os.getenv("PGPASSWORD")
host = "localhost"
port = "5432"
database = "url_shortener"

DATABASE_URL = (
    f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
