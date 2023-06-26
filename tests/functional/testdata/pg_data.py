import uuid
import random
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash("Secret123")

users = [
    {
        "first_name": f"Name-{i}",
        "last_name": f"Surname-{i}",
        "disabled": False,
        "email": f"user-{i}@example.com",
        "password": f"{hashed_password}"
    } for i in range(50)]

roles = [
    {
        'title': 'admin',
        'permissions': 7
    },
    {
        'title': 'content-manager',
        'permissions': 5
    },
    {
        'title': 'subscriber',
        'permissions': 3
    },
    {
        'title': 'viewer',
        'permissions': 1
    },
]
