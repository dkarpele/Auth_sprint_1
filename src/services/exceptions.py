from fastapi import HTTPException, status

credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
)

re_login_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your credentials expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
)

access_token_invalid_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired. Create new token with /refresh",
            headers={"WWW-Authenticate": "Bearer"},
)


wrong_username_or_password = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
)


def entity_doesnt_exist(name: str, value: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"{name} {value} doesn't exist",
        headers={"WWW-Authenticate": "Bearer"},
    )
