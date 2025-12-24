from fastapi import FastAPI

from .routes.api import inventory_router

app = FastAPI()

app.include_router(inventory_router)


@app.get("/")
async def home():
    return "Hello"
