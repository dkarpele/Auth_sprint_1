import os
import logging

from sqlalchemy import create_engine
import typer

from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
from sqlalchemy.future import select

from sqlalchemy.orm import sessionmaker


from core.config import database_dsn
from models.entity import User
from models.roles import UserRole, Role
from schemas.entity import UserSignUp

load_dotenv()


def main():
    try:
        logging.info('Creating Admin...')
        url = f'postgresql://' \
              f'{database_dsn.user}:{database_dsn.password}@'\
              f'{database_dsn.host}:{database_dsn.port}/'\
              f'{database_dsn.dbname}'
        echo = (os.getenv('ENGINE_ECHO', 'False') == 'True')
        engine = create_engine(url, echo=echo)

        maker = sessionmaker(bind=engine)
        session = maker()

        user_data = UserSignUp(email=os.environ.get('ADMIN_EMAIL',
                                                    'admin@example.com'),
                               password=os.environ.get('ADMIN_PASSWORD',
                                                       'Secret123'),
                               first_name='admin',
                               last_name='admin',)

        admin = session.execute(
            select(Role).
            filter(Role.title == 'admin')
        )
        if not admin.scalars().first():
            data = [User(**jsonable_encoder(user_data)),
                    Role('admin', 7)]
            for el in data:
                session.add(el)
                session.commit()
                session.refresh(el)

            user_role = UserRole(user_id=data[0].id,
                                 role_id=data[1].id)
            session.add(user_role)
            session.commit()
            session.refresh(user_role)
            logging.info('Admin created successfully.')
        else:
            logging.info('Admin already exists. Nothing to do.')
    except ConnectionRefusedError:
        logging.error("Нет подключения к БД")


if __name__ == '__main__':
    typer.run(main)
