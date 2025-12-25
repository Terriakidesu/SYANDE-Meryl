from datetime import datetime

from pydantic import BaseModel


class Role(BaseModel):
    role_id: int
    role_name: str


class Permission(BaseModel):
    permission_id: int
    permission_code: str
    description: str
    category: str


class User(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    username: str
    password: str
    created_at: datetime


class UserForm(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    username: str


class Phone(BaseModel):
    phone_id: int
    user_id: int
    phone: str


class Email(BaseModel):
    email_id: int
    user_id: int
    email: str


class RolePermission(BaseModel):
    role_id: int
    permission_id: int


class UserRole(BaseModel):
    user_id: int
    role_id: int
