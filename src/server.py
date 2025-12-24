from fastapi import FastAPI

from .routes.api import (
    inventory_router,
    management_router,
    sales_router,
    users_router
)

app = FastAPI()

app.include_router(management_router)
app.include_router(inventory_router)
app.include_router(users_router)
app.include_router(sales_router)


@app.get("/")
async def home():
    return "Hello"
