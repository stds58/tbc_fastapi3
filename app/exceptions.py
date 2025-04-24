from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging


logger = logging.getLogger(__name__)

# Пользовательские исключения
class CustomNotFoundException(HTTPException):
    def __init__(self, detail: str = "Ресурс не найден"):
        super().__init__(status_code=404, detail=detail)

class CustomBadRequestException(HTTPException):
    def __init__(self, detail: str = "Неверный запрос"):
        super().__init__(status_code=400, detail=detail)

class CustomInternalServerException(HTTPException):
    def __init__(self, detail: str = "Внутренняя ошибка сервера"):
        super().__init__(status_code=500, detail=detail)

class TokenExpiredException(HTTPException):
    def __init__(self, detail: str = "Токен истек"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class NoJwtException(HTTPException):
    def __init__(self, detail: str = "JWT-токен отсутствует"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class NoUserIdException(HTTPException):
    def __init__(self, detail: str = "Идентификатор пользователя отсутствует"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Доступ запрещен"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


# Обработчики исключений
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"Ошибка целостности данных: {exc.orig}")
    return JSONResponse(
        status_code=400,
        content={"error": f"Ошибка целостности данных: {exc.orig}"},
    )

# async def sqlalchemy_error_handler(request: Request, exc: Exception):
#     # Логирование ошибки (необязательно)
#     print(f"SQLAlchemyError: {exc}")
#     return JSONResponse(
#         status_code=500,
#         content={"error": "Ошибка базы данных"},
#     )

async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Ошибка базы данных: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Внутренняя ошибка сервера"},
    )

