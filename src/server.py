from fastapi import FastAPI, Request

from .routes.api import (
    auth_router,
    inventory_router,
    management_router,
    sales_router,
    users_router
)

app = FastAPI()

app.include_router(auth_router)
app.include_router(management_router)
app.include_router(inventory_router)
app.include_router(users_router)
app.include_router(sales_router)


@app.get("/")
async def home():
    return "Hello"


@app.get("/endpoints")
async def list_endpoints(request: Request):
    url_list = [
        f"{route.methods} - {route.path}" for route in request.app.routes
    ]

    return url_list
