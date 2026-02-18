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

# What if we used = Session()?
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Need to understand this + Can we do a begin once style?
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
