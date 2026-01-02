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
    shoe_id: int
    size_id: int
    variant_stock: int


class Shoe(BaseModel):
    shoe_id: int
    shoe_name: str
    brand_id: int
    markup: int
    shoe_price: float
    first_sale_at: datetime
    created_at: datetime


class shoeForm(BaseModel):
    shoe_name: str
    brand_id: int
    category_id: int
    markup: int
    shoe_price: float
    first_sale_at: datetime
