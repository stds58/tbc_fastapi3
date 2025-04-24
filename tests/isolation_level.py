import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, update
from app.dictionaries.models import Manufacturer as SomeModel
from app.session_maker import connection, connection2

# python isolation_level.py

DATABASE_URL = "postgresql+asyncpg://admin:admin@localhost:6432/fast_api"
engine = create_async_engine(DATABASE_URL, echo=True)
async_sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

# Функция с использованием @connection
@connection(isolation_level="SERIALIZABLE", commit=False)
async def test_with_connection(session: AsyncSession):
    # Транзакция A: Начинаем обновление записи
    await session.execute(update(SomeModel).where(SomeModel.id == 1).values(access_id=1))
    # Не фиксируем изменения (не вызываем commit)

    # Транзакция B: Читаем запись
    result = await session.execute(select(SomeModel).where(SomeModel.id == 1))
    record = result.scalar_one_or_none()
    print(f"Значение в транзакции B (connection): {record.access_id}")

    # Фиксируем изменения в транзакции A
    await session.commit()

    # Транзакция B: Читаем запись снова
    result = await session.execute(select(SomeModel).where(SomeModel.id == 1))
    record = result.scalar_one_or_none()
    print(f"Значение в транзакции B после commit (connection): {record.access_id}")


# Функция с использованием @connection2
@connection2(isolation_level="SERIALIZABLE", commit=False)
async def test_with_connection2(session: AsyncSession):
    # Транзакция A: Начинаем обновление записи
    await session.execute(update(SomeModel).where(SomeModel.id == 1).values(access_id=2))
    # Не фиксируем изменения (не вызываем commit)

    # Транзакция B: Читаем запись
    result = await session.execute(select(SomeModel).where(SomeModel.id == 1))
    record = result.scalar_one_or_none()
    print(f"Значение в транзакции B (connection2): {record.access_id}")

    # Фиксируем изменения в транзакции A
    await session.commit()

    # Транзакция B: Читаем запись снова
    result = await session.execute(select(SomeModel).where(SomeModel.id == 1))
    record = result.scalar_one_or_none()
    print(f"Значение в транзакции B после commit (connection2): {record.access_id}")


async def test_with_connection_and_parallel_sessions():
    # Создаем две независимые сессии
    session_a = async_sessionmaker()
    session_b = async_sessionmaker()

    async with session_a, session_b:
        # Устанавливаем уровень изоляции для обеих сессий
        await session_a.connection(execution_options={"isolation_level": "SERIALIZABLE"})
        await session_b.connection(execution_options={"isolation_level": "SERIALIZABLE"})

        # Транзакция A: Начинаем обновление записи
        await session_a.execute(update(SomeModel).where(SomeModel.id == 1).values(access_id=3))
        # Не фиксируем изменения (не вызываем commit)

        # Транзакция B: Читаем запись
        result = await session_b.execute(select(SomeModel).where(SomeModel.id == 1))
        record = result.scalar_one_or_none()
        print(f"Значение в транзакции B (parallel): {record.access_id}")

        # Фиксируем изменения в транзакции A
        await session_a.commit()

        # Транзакция B: Читаем запись снова
        result = await session_b.execute(select(SomeModel).where(SomeModel.id == 1))
        record = result.scalar_one_or_none()
        print(f"Значение в транзакции B после commit (parallel): {record.access_id}")


async def main():
    # Тест с @connection
    print("Тестируем @connection:")
    await test_with_connection()

    # Тест с @connection2
    print("\nТестируем @connection2:")
    await test_with_connection2()

    # Тест с параллельными сессиями
    print("\nТестируем параллельные сессии:")
    await test_with_connection_and_parallel_sessions()


if __name__ == "__main__":
    asyncio.run(main())


# python isolation_level.py

