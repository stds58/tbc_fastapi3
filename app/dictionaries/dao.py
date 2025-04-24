# В этот файл мы будем выносить индивидуальные функции, относящиеся к конкретной сущности.
# К примеру такой сущностью может выступить наши студенты и функции базы данных, которые относятся исключительно к студентам.
# DAO в контексте баз данных расшифровывается как «Data Access Object» (объект доступа к данным),
# поэтому я привык называть этот файл именно service.py. В других проектах вы можете встретить название core.py или service.py.
# Тут как кому удобно.


from typing import Optional, List, Dict, TypeVar, Any
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.dictionaries.models import Product, Manufacturer, DimensionUnit, Subcategory, Category
from app.database import async_session_maker


class ManufacturerDAO:
    @classmethod
    async def find_all_manufacturers(cls):
        async with async_session_maker() as session:
            query = select(Manufacturer)
            manufacturers = await session.execute(query)
            return manufacturers.scalars().all()






