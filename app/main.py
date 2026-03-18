from fastapi import FastAPI

from app.api.routes import login, users, urls

app = FastAPI()
app.include_router(login.router)
app.include_router(users.router)
app.include_router(urls.router)
app.include_router(urls.redirect_router)
