#класс с универсальными методами по работе с базой данных.
from typing import Optional, List, Dict, TypeVar, Any, Generic, AsyncGenerator
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, class_mapper, declarative_base
from fastapi import HTTPException
from pydantic import BaseModel
from app.dictionaries.models import Product, Manufacturer, DimensionUnit, Subcategory, Category
from app.dictionaries.schemas import SManufacturerFilter, SProductFilter
from app.database import async_session_maker
from app.session_maker import connection
import logging



logger = logging.getLogger(__name__)

Base = declarative_base()
ModelType = TypeVar("ModelType", bound=Base) # мы можем задать границу типа, т.о. мы будем уверены при статическом анализе что использованы верные типы как минимум в иерархии
FilterType = TypeVar("FilterType", bound=BaseModel)  # Модель фильтра


class BaseDAO(Generic[ModelType, FilterType]):
    model: type[ModelType]  # Должен быть переопределен в дочерних классах

    @classmethod
    @connection(isolation_level="READ COMMITTED", commit=False)
    async def find_all(cls, session: AsyncSession, **filter_by) -> List[ModelType]:
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    @connection(isolation_level="READ COMMITTED", commit=False)
    async def find_all_opt(cls, session: AsyncSession, options: Optional[List[Any]] = None, filters: FilterType = None) -> List[ModelType]:
        query = select(cls.model)
        if filters is not None:
            filter_dict = filters.model_dump(exclude_unset=True)  # Для Pydantic v2
            # filter_dict = filters.dict(exclude_unset=True)    # Для Pydantic v1
            filter_dict = {key: value for key, value in filter_dict.items() if value is not None}
            query = query.filter_by(**filter_dict)
        if options:
            query = query.options(*options)
        result = await session.execute(query)
        results = result.unique().scalars().all()  # Получаем все записи
        if len(results) == 0:  # Проверяем количество найденных записей
            raise HTTPException(status_code=404, detail=f"Найдено 0 записей")
        return results

    @classmethod
    async def find_all_stream(cls, session: AsyncSession, options: Optional[List[Any]] = None,filters: FilterType = None) -> AsyncGenerator[ModelType, None]:
        query = select(cls.model)
        if filters is not None:
            filter_dict = filters.model_dump(exclude_unset=True)
            filter_dict = {key: value for key, value in filter_dict.items() if value is not None}
            query = query.filter_by(**filter_dict)
        if options:
            query = query.options(*options)
        stream = await session.stream_scalars(query)
        async for record in stream:
            yield record

    @classmethod
    @connection(isolation_level="READ COMMITTED", commit=False)
    async def find_one_or_none(cls, session: AsyncSession, options: Optional[List[Any]] = None, filters: FilterType = None) -> Optional[ModelType]:
        query = select(cls.model)
        if filters is not None:
            filter_dict = filters.model_dump(exclude_unset=True)
            filter_dict = {key: value for key, value in filter_dict.items() if value is not None}
            query = query.filter_by(**filter_dict)
        if options:
            query = query.options(*options)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    @connection(isolation_level="READ COMMITTED", commit=False)
    async def find_one_or_none_by_id(cls, data_id: int, session: AsyncSession):
        return await session.get(cls.model, data_id)

    @classmethod
    @connection(isolation_level="READ COMMITTED")
    async def add(cls, session: AsyncSession, **values) -> ModelType:
        new_instance = cls.model(**values)
        session.add(new_instance)
        await session.flush()
        return new_instance

    @classmethod
    @connection(isolation_level="READ COMMITTED")
    async def update(cls, session: AsyncSession, filter_by, **values) -> Optional[List[ModelType]]:
        query = (
            sqlalchemy_update(cls.model)
            .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
            .values(**values)
            .execution_options(synchronize_session="fetch")
        )
        result = await session.execute(query)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Обновлено 0 записей")
        else:
            await session.flush()
        # await session.refresh(result)
        return result

    @classmethod
    @connection(isolation_level="READ COMMITTED")
    async def update_many(cls, session: AsyncSession, filters: Optional[FilterType] = None, values: Optional[ModelType] = None) -> int:
        if filters is not None:
            filter_dict = filters.model_dump(exclude_unset=True)
        else:
            filter_dict = {}
        if values is None:
            raise ValueError("Параметр 'values' не может быть None")
        values_dict = values.model_dump(exclude_unset=True)
        stmt = (
            sqlalchemy_update(cls.model)
            .filter_by(**filter_dict)
            .values(**values_dict)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount

    @classmethod
    @connection(isolation_level="READ COMMITTED")
    async def update_one_by_id(cls, session: AsyncSession, data_id: int, values: BaseModel) -> Optional[ModelType]:
        # Получаем запись по ID
        record = await session.get(cls.model, data_id)
        if not record:
            return None  # Если запись не найдена, возвращаем None
        # Обновляем поля записи
        values_dict = values.model_dump(exclude_unset=True)
        for key, value in values_dict.items():
            setattr(record, key, value)
        # Фиксируем изменения в базе данных
        await session.flush()
        return record  # Возвращаем обновленную запись

    @classmethod
    @connection(isolation_level="READ COMMITTED")
    async def delete(cls, session: AsyncSession, id: int) -> dict:
        query = sqlalchemy_delete(cls.model).filter_by(id=id)
        result = await session.execute(query)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Объект с ID {id} не найден")
        return {"message": f"Объект с id {id} удален!", "deleted_count": result.rowcount}

    @classmethod
    def to_dict(self) -> dict:
        """Универсальный метод для конвертации объекта SQLAlchemy в словарь"""
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}


# Python < 3.12:
# import typing
# T = typing.TypeVar("T", bound=Base) # мы можем задать границу типа, т.о. мы будем уверены при статическом анализе что использованы верные типы как минимум в иерархии
# class BaseDAO(typing.Generic[T]):
#     model: type[T]
# Python >= 3.12:
# # точно так же можно задать границу дженерика
# class BaseDAO[T: Base]:
#     model: type[T]


class ManufacturerDAO(BaseDAO[Manufacturer, SManufacturerFilter]):
    model = Manufacturer

class ProductDAO(BaseDAO[Product, SProductFilter]):
    model = Product



