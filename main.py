from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from app.dictionaries.router import router as router_manufacturers
from app.users.router import router as router_users
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.exceptions import http_exception_handler,sqlalchemy_error_handler,integrity_error_handler
from app.pages.router import router as router_pages
from app.keycloak.keycloak import KeycloakManager, get_keycloak_manager, User
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings


app = FastAPI()

# Для работы с сессиями (OAuth нужен session middleware)
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_MIDDLEWARE_SECRET_KEY)
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     body = await request.body()
#     print(f"Request body: {body}")
#     response = await call_next(request)
#     return response

# Регистрация обработчиков исключений
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)

@app.get("/")
def home_page():
    return {"message": "Привет, Хабр!"}

app.mount('/static', StaticFiles(directory='static'), 'static')

app.include_router(router_users)
app.include_router(router_manufacturers)
app.include_router(router_pages)


keycloak_manager = KeycloakManager(keycloak_url="http://localhost:8080", realm="tbcrealm")

async def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
    # C:\tbc_fastapi\.venv\Scripts\uvicorn.exe main:app


