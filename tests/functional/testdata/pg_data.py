from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash("Secret123")
users = [{
        "id": "e9756a00-73d6-455c-8bfa-734d859867b0",
        "first_name": f"Admin",
        "last_name": f"Admin",
        "disabled": False,
        "email": f"admin@example.com",
        "password": f"{hashed_password}"
    }]
users.extend([
    {
        "first_name": f"Name-{i}",
        "last_name": f"Surname-{i}",
        "disabled": False,
        "email": f"user-{i}@example.com",
        "password": f"{hashed_password}"
    } for i in range(50)])

roles = [
    {
        'id': 'c1c3c6fc-95df-49cd-81f1-873f0128c404',
        'title': 'admin',
        'permissions': 7
    },
    {
        'id': '0a1af085-c8c4-49c0-8407-6f032589e614',
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

users_roles = [
    {
        'id': 'ccdb4cbe-7859-43af-8188-27875d9d273a',
        'user_id': 'e9756a00-73d6-455c-8bfa-734d859867b0',
        'role_id': 'c1c3c6fc-95df-49cd-81f1-873f0128c404'
    },
]
