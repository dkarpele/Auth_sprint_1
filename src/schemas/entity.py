from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, constr
from core import config

password_regex = "^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"


class UserEmail(BaseModel):
    email: EmailStr


class UserLogin(UserEmail):
    password: constr(min_length=8,
                     max_length=50,
                     regex=password_regex)


class UserData(BaseModel):
    first_name: str = Field(...,
                            description=config.FIRST_NAME_DESC,
                            min_length=3,
                            max_length=50
                            )
    last_name: str = Field(...,
                           description=config.LAST_NAME_DESC,
                           min_length=3,
                           max_length=50)


class UserSignUp(UserLogin, UserData):
    ...


class UserResponseData(UserEmail, UserData):
    id: UUID

    class Config:
        orm_mode = True


class UserInDB(UserEmail, UserData):
    id: UUID
    # It's a hashed password
    hashed_password: str = Field(..., alias="password")

