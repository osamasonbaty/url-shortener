from fastapi import FastAPI

from app.core.db import Base, engine
from app.api.routes import login, users, urls

app = FastAPI()
app.include_router(login.router)
app.include_router(users.router)
app.include_router(urls.router)
app.include_router(urls.redirect_router)


# TODO: How do we handle this professionally
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
