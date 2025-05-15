from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from app.dictionaries.router import router as router_manufacturers
from app.users.router import router as router_users
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.exceptions import http_exception_handler,sqlalchemy_error_handler,integrity_error_handler
from app.pages.router import router as router_pages
from app.keycloak.keycloak import get_keycloak_manager, User
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings


app = FastAPI()

# Для работы с сессиями (OAuth нужен session middleware)
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_MIDDLEWARE_SECRET_KEY)

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

@app.get("/protected")
async def protected_route(user: User = Depends(get_keycloak_manager().get_user_from_token)):
    return {"message": "You are authenticated", "user": user}

# @app.get("/protected")
# async def protected_route():
#     return {"message": "You are authenticated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
    # C:\tbc_fastapi\.venv\Scripts\uvicorn.exe main:app


