from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from fastapi.templating import Jinja2Templates
from pathlib import Path


logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = Path(__file__).parent.parent
templates = Jinja2Templates(directory=PROJECT_DIR / "app/templates")


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


from app.config import settings
from authlib.integrations.starlette_client import OAuth
oauth = OAuth()

oauth.register(
    name='keycloak',
    client_id=settings.KEYCLOAK_CLIENT_ID,
    client_secret=settings.KEYCLOAK_CLIENT_SECRET,
    server_metadata_url=f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/.well-known/openid-configuration",
    redirect_uri=f"{settings.FRONT_URL}/auth/callback/",
    client_kwargs={'scope': 'openid profile email'}
)
# Настройка Keycloak
KEYCLOAK_URL = settings.KEYCLOAK_URL
KEYCLOAK_REALM = settings.KEYCLOAK_REALM
KEYCLOAK_CLIENT_ID = settings.KEYCLOAK_CLIENT_ID
KEYCLOAK_CLIENT_SECRET = settings.KEYCLOAK_CLIENT_SECRET # удалить, если Access Type = public
KEYCLOAK_ADMIN = settings.KEYCLOAK_ADMIN
KEYCLOAK_ADMIN_PASSWORD = settings.KEYCLOAK_ADMIN_PASSWORD
MASTER_REALM = "master"

# Обработчики исключений
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.headers and 'Location' in exc.headers:
        return RedirectResponse(url=exc.headers['Location'], status_code=exc.status_code)
    # if exc.status_code == 401:  # Ошибка аутентификации
    #     return templates.TemplateResponse(
    #         name='login.html',
    #         context={'request': request}
    #     )
        # return templates.TemplateResponse(
        #     name='error.html',
        #     context={'request': request,
        #              'error_message': "JWT-токен отсутствует или не валиден",
        #              'login_url': request.url_for('login')  # Генерация URL для страницы входа
        #              }
        # )
    else:
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

class IncorrectEmailOrPasswordException(HTTPException):
    def __init__(self, detail: str = "Неверный email или пароль", status_code: int = 401):
        super().__init__(status_code=status_code, detail=detail)


