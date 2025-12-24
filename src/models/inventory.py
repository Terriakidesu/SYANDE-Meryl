from datetime import datetime

from pydantic import BaseModel


class Brand(BaseModel):
    brand_id: int
    brand_name: str


class Category(BaseModel):
    category_id: int
    category_name: str


class Size(BaseModel):
    size_id: int
    size: float
    sizing_system: str


class Variant(BaseModel):
    variant_id: int
    product_id: int
    size_id: int
    variant_stock: int


class Product(BaseModel):
    product_id: int
    product_name: str
    brand_id: int
    category_id: int
    product_price: float
    first_sale_at: datetime
    created_at: datetime


class ProductForm(BaseModel):
    product_name: str
    brand_id: int
    category_id: int
    product_price: float
    first_sale_at: datetime
