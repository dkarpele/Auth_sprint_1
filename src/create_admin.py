import os
import asyncio
import logging

from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
from sqlalchemy.future import select

from core.config import database_dsn
from db import postgres
from models.entity import User
from models.roles import UserRole, Role
from schemas.entity import UserSignUp

load_dotenv()


async def main():
    try:
        db = postgres.Postgres(
            f'postgresql+asyncpg://'
            f'{database_dsn.user}:{database_dsn.password}@'
            f'{database_dsn.host}:{database_dsn.port}/'
            f'{database_dsn.dbname}')
        async with db.async_session() as session:
            admin = await session.execute(
                select(Role).
                filter(Role.title == 'admin')
            )
            if not admin.scalars().all():
                data = []
                data.append(Role('admin', 7))
                data.append(User(**jsonable_encoder(
                    UserSignUp(email=os.environ.get('ADMIN_EMAIL', 'admin@example.com'),
                               first_name='admin',
                               last_name='admin',
                               password=os.environ.get('ADMIN_PASSWORD', 'Secret123')))))
                data.append(UserRole(user_id=data[0].id, role_id=data[1].id))
                for el in data:
                    session.add(el)
                    await session.commit()
                    await session.refresh(el)
    except ConnectionRefusedError:
        logging.error("Нет подключения к БД")


if __name__ == '__main__':
    asyncio.run(main())
