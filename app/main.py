from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from app.dictionaries.router import router as router_manufacturers
from app.users.router import router as router_users
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from exceptions import http_exception_handler,sqlalchemy_error_handler,integrity_error_handler
from app.pages.router import router as router_pages


app = FastAPI()


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




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", reload=True)
    # C:\tbc_fastapi\.venv\Scripts\uvicorn.exe main:app


