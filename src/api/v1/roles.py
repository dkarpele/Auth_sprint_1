from fastapi.encoders import jsonable_encoder

from http import HTTPStatus
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.entity import User
from db.postgres import get_session
from schemas.entity import UserInDB, UserLogin

# Объект router, в котором регистрируем обработчики
router = APIRouter()