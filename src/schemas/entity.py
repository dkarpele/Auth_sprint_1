from uuid import UUID

from pydantic import BaseModel, Field
from core import config

password_regex = "^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"


class UserCreate(BaseModel):
    login: str = Field(...,
                       description=config.LOGIN_DESC,
                       min_length=3,
                       max_length=50)
    password: str = Field(...,
                          description=config.PASSWORD_DESC,
                          min_length=8,
                          max_length=50,
                          regex=password_regex)
    first_name: str = Field(...,
                            description=config.FIRST_NAME_DESC,
                            min_length=3,
                            max_length=50)
    last_name: str = Field(...,
                           description=config.LAST_NAME_DESC,
                           min_length=3,
                           max_length=50)


class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        orm_mode = True
