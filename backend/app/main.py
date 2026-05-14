from fastapi import FastAPI
from app.db import Base, engine
from app.routers import users, items

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(items.router)