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

def get_connection():
    with engine.connect() as connection:
        yield connection

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# FastAPI-specific
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
