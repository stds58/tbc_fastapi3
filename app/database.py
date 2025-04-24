from datetime import datetime
from typing import Annotated, Optional
from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy import String, Boolean, ForeignKey
from fastapi import HTTPException
from app.config import get_db_url
import logging


logger = logging.getLogger(__name__)

# create_async_engine: создаёт асинхронное подключение к базе данных PostgreSQL, используя драйвер asyncpg.
# async_session_maker: создаёт фабрику асинхронных сессий, используя созданный движок.
# Сессии используются для выполнения транзакций в базе данных.
# Base: абстрактный класс, от которого наследуются все модели.
# Он используется для миграций и аккумулирует информацию обо всех моделях,
# чтобы Alembic мог создавать миграции для синхронизации структуры базы данных с моделями на бэкенде.·
# @declared_attr.directive: определяет имя таблицы для модели на основе имени класса,
# преобразуя его в нижний регистр и добавляя букву 's' в конце (например, класс User будет иметь таблицу users).

DATABASE_URL = get_db_url()
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# def connection(method):
#     async def wrapper(*args, **kwargs):
#         async with async_session_maker() as session:
#             try:
#                 # Явно не открываем транзакции, так как они уже есть в контексте
#                 return await method(*args, session=session, **kwargs)
#             except IntegrityError as e:
#                 logger.error(f"Ошибка целостности данных: {e.orig}")
#                 raise HTTPException(status_code=400, detail=f"Ошибка целостности данных: {e.orig}")
#             except SQLAlchemyError as e:
#                 logger.error(f"Ошибка при работе с базой данных: {e}")
#                 raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
#             except Exception as e:
#                 await session.rollback()  # Откатываем сессию при ошибке
#                 raise e  # Поднимаем исключение дальше
#             finally:
#                 await session.close()  # Закрываем сессию
#     return wrapper


# настройка аннотаций
int_pk = Annotated[int, mapped_column(primary_key=True)]
access_id = Annotated[int, mapped_column(nullable=True, info={"verbose_name": "id в аксесе Блага"})]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=func.now())]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]
str_255 = Annotated[str, mapped_column(String(255), nullable=True)]
bool_null_false = Annotated[bool, mapped_column(default=False, server_default=text("'false'"), nullable=False)]

def fk_protect_nullable(table_name: str):
    return Annotated[
        Optional[int],
        mapped_column(
            ForeignKey(f"{table_name}.id", ondelete="PROTECT"),
            nullable=True
        )
    ]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True  # Класс абстрактный, чтобы не создавать отдельную таблицу для него

    # id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    access_id: Mapped[access_id]

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
        #return f"{cls.__name__.lower()}s"
        #return cls.__name__.lower() + 's'




# DeclarativeBase:
#     Основной класс для всех моделей, от которого будут наследоваться все таблицы (модели таблиц).
#     Эту особенность класса мы будем использовать неоднократно.
# AsyncAttrs:
#     Позволяет создавать асинхронные модели, что улучшает производительность при работе с асинхронными операциями.
# create_async_engine:
#     Функция, создающая асинхронный движок для соединения с базой данных по предоставленному URL.
# async_sessionmaker:
#     Фабрика сессий для асинхронного взаимодействия с базой данных. Сессии используются для выполнения запросов и транзакций.


