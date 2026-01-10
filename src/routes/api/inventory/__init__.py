from .brands import brands_router
from .categories import categories_router
from .shoes import shoes_router
from .sizes import sizes_router
from .variants import variants_router

__all__ = [
    "shoes_router",
    "brands_router",
    "categories_router",
    "sizes_router",
    "variants_router",
]

from fastapi import APIRouter

inventory_router = APIRouter(prefix="/inventory")

inventory_router.include_router(shoes_router)
inventory_router.include_router(brands_router)
inventory_router.include_router(categories_router)
inventory_router.include_router(sizes_router)
inventory_router.include_router(variants_router)
