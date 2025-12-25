from datetime import datetime

from pydantic import BaseModel


class Sale(BaseModel):
    sale_id: int
    user_id: int
    customer_name: str
    total_amount: float
    cash_received: float
    change_amount: float
    sales_date: datetime


class Sales_Item(BaseModel):
    sale_item_id: int
    sale_id: int
    variant_id: int
    markup: int
    quantity: int
    price: float


class Return(BaseModel):
    return_id: int
    sale_id: int
    customer_name: str
    return_reason: str
    total_refund: float
    return_date: datetime
