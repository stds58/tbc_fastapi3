from contextlib import asynccontextmanager
from functools import wraps
from typing import Optional, Callable, Any, AsyncGenerator
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from fastapi import HTTPException
import logging



logger = logging.getLogger(__name__)


@asynccontextmanager
async def get_session_with_isolation(session_factory, isolation_level: Optional[str] = None) -> AsyncGenerator[AsyncSession, None]:
    """
    Контекстный менеджер для создания сессии с опциональным уровнем изоляции.
    """
    async with session_factory() as session:
        if isolation_level:
            await session.connection(execution_options={"isolation_level": isolation_level})
            # Проверяем уровень изоляции
            result = await session.execute(text("SHOW TRANSACTION ISOLATION LEVEL;"))
            current_isolation_level = result.scalar()
            print(f"Текущий уровень изоляции: {current_isolation_level}")
        yield session


def connection(isolation_level: Optional[str] = None, commit: bool = True):
    """
    Декоратор для управления сессией с возможностью настройки уровня изоляции и коммита.
    """
    def decorator(method: Callable[..., Any]):
        @wraps(method)
        async def wrapper(*args, **kwargs):
            async with get_session_with_isolation(async_session_maker, isolation_level) as session:
                try:
                    result = await method(*args, session=session, **kwargs)
                    if commit:
                        await session.commit()
                    return result
                except IntegrityError as e:
                    logger.error(f"Ошибка целостности данных: {e.orig}")
                    raise HTTPException(status_code=400, detail=f"Ошибка целостности данных: {e.orig}")
                except SQLAlchemyError as e:
                    logger.error(f"Ошибка при работе с базой данных: {e}")
                    raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
                except Exception as e:
                    await session.rollback()
                    raise
        return wrapper
    return decorator


def connection2(isolation_level: Optional[str] = None, commit: bool = True):
    def decorator(method):
        @wraps(method)
        async def wrapper(*args, **kwargs):
            async with async_session_maker() as session:
                try:
                    if isolation_level:
                        await session.execute(text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"))
                        # Проверяем уровень изоляции
                        result = await session.execute(text("SHOW TRANSACTION ISOLATION LEVEL;"))
                        current_isolation_level = result.scalar()
                        print(f"Текущий уровень изоляции: {current_isolation_level}")
                    result = await method(*args, session=session, **kwargs)
                    if commit:
                        await session.commit()
                    return result
                except IntegrityError as e:
                    logger.error(f"Ошибка целостности данных: {e.orig}")
                    raise HTTPException(status_code=400, detail=f"Ошибка целостности данных: {e.orig}")
                except SQLAlchemyError as e:
                    logger.error(f"Ошибка при работе с базой данных: {e}")
                    raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
                except Exception as e:
                    await session.rollback()
                    raise
                finally:
                    await session.close()
        return wrapper
    return decorator



# """
#     Декоратор для управления сессией с возможностью настройки уровня изоляции и коммита.
#     Параметры:
#     - `isolation_level`: уровень изоляции для транзакции (например, "SERIALIZABLE").
#     - `commit`: если `True`, выполняется коммит после вызова метода.
#     READ COMMITTED — для обычных запросов (по умолчанию в PostgreSQL).
#     SERIALIZABLE — для финансовых операций, требующих максимальной надежности.
#     REPEATABLE READ — для отчетов и аналитики.
#
#     # Чтение данных
#     @connection(isolation_level="READ COMMITTED")
#     async def get_user(self, session, user_id: int):
#         ...
#     # Финансовая операция
#     @connection(isolation_level="SERIALIZABLE", commit=False)
#     async def transfer_money(self, session, from_id: int, to_id: int):
#         ...
#     """

