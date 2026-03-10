import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL

load_dotenv()


class Base(DeclarativeBase):
    pass


# TODO: Use Pydantic Settings. Can Also add URL creation from sqlalchemy
# Ref: https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/app/core/db.py
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    db_type = os.getenv("DB_TYPE", "sqlite+pysqlite")
    database = os.getenv("DB_NAME", "url_shortener")

    if db_type.startswith("sqlite"):
        sqlite_database = database if database.endswith(".db") else f"{database}.db"
        DATABASE_URL = f"{db_type}:///{sqlite_database}"
    else:
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "5432"))

        if not password:
            raise RuntimeError("DB_PASSWORD is not set")

        DATABASE_URL = URL.create(
            drivername=db_type,
            username=user,
            password=password,
            host=host,
            port=port,
            database=database,
        )

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine)


# Define in deps.py
# Ref: https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/app/api/deps.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
