
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ...includes import Database

inventory_router = APIRouter(prefix="/api/inventory")

db = Database()


@inventory_router.get("/items", response_class=JSONResponse)
async def list_items(request: Request):

    # db.connect()

    return db.fetchAll("SELECT * from Products")
