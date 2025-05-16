from fastapi import APIRouter, Depends, HTTPException, Body, Path
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from typing import List, Optional
from app.database import async_session_maker
from app.dictionaries.models import Product, Manufacturer, DimensionUnit, Subcategory, Category
from app.dictionaries.services.base import ManufacturerDAO, ProductDAO
from app.dictionaries.schemas import SManufacturer, SManufacturerAdd, SManufacturerUpdate, SManufacturerUpdateById, SManufacturerFilter, SProduct, SProductAdd
from app.dictionaries.filtr import FiltrProduct, FiltrManufacturer
from app.dictionaries.service import fetch_all_manufacturers
from app.session_maker import get_session_with_isolation
from app.users.router import verify_keycloak_token


# from  fastapi import APIRouter:
#     Импортирует APIRouter из FastAPI, который используется для создания маршрутов (routes) для вашего API.
# from  sqlalchemy.future import select:
#     Импортирует функцию select из SQLAlchemy для создания  SELECT запросов к базе данных (получение данных).
# from  app.database import async_session_maker:
#     Импортирует async_session_maker, который используется для создания асинхронных сессий с базой данных.


router = APIRouter(prefix='/dictionaries', tags=['справочник производителей'])
# tags=['справочник производителей']: Добавляет тег к роутеру, который будет использоваться в документации Swagger для группировки и описания маршрутов.

# @router.get("/", summary="Получить всех производителей")
# async def get_all_manufacturers():
#     async with async_session_maker() as session:
#         query = select(Manufacturer)
#         result = await session.execute(query)
#         manufacturers = result.scalars().all()
#         return manufacturers
# # Список студентов возвращается в виде JSON-ответа. FastAPI автоматически преобразует его в формат JSON.


async def generate_data(session, filters: Optional[SManufacturerFilter] = None):
    """Генератор для потоковой передачи данных."""
    async for record in ManufacturerDAO.find_all_stream(session=session, filters=filters):  # Используем await
        pydantic_record = SManufacturer.model_validate(record)  # Преобразуем ORM-объект в Pydantic
        yield pydantic_record.model_dump_json() + "\n" # Каждая запись в формате JSON, разделенная новой строкой

@router.get("/manufacturers/stream/download", summary="Потоковая передача данных о производителях")
async def get_manufacturers_stream_download(request_body: SManufacturerFilter = Depends()):
    async with get_session_with_isolation(async_session_maker, isolation_level="READ COMMITTED") as session:
        return StreamingResponse(
            generate_data(session, filters=request_body),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=manufacturers.json"}
        )

@router.get("/manufacturers/stream/", summary="Потоковая передача данных о производителях")
async def get_manufacturers_stream(request_body: SManufacturerFilter = Depends()):
    async with get_session_with_isolation(async_session_maker, isolation_level="READ COMMITTED") as session:
        records = []
        async for record in ManufacturerDAO.find_all_stream(session=session, filters=request_body):
            pydantic_record = SManufacturer.model_validate(record)  # Преобразуем ORM-объект в Pydantic
            records.append(pydantic_record.model_dump())  # Преобразуем в словарь
        if not records:
            raise HTTPException(status_code=404, detail="Найдено 0 записей")
        return records

@router.get("/manufacturers/", summary="Получить всех производителей", response_model=List[SManufacturer])
async def get_all_manufacturers(
        request_body: SManufacturerFilter = Depends(),
        user: dict = Depends(verify_keycloak_token),
        ) -> list[SManufacturer]:
    print('user2222 ',user)
    manufacturers = await fetch_all_manufacturers(request_body)
    return manufacturers
    #return await ManufacturerDAO.find_all_opt(options=None,filters=request_body)


@router.get("/manufacturers/{id}", summary="Получить одого производителя")
async def get_manufacturer_by_filter(request_body: SManufacturerFilter = Depends()) -> SManufacturer | dict:
    result = await ManufacturerDAO.find_one_or_none(options=None,filters=request_body)
    if result is None:
        return {'message': f'Производитель с указанными вами параметрами не найден!'}
    return result

@router.get("/manufacturers/by_id/{id}", summary="Получить одого производителя по id", response_model=SManufacturer)
async def get_manufacturer_by_id(id: int = Path(..., description="ID производителя")) -> SManufacturer | dict:
    result = await ManufacturerDAO.find_one_or_none_by_id(data_id=id)
    if result is None:
        raise HTTPException(status_code=404, detail="Производитель с указанным ID не найден")
    return result

@router.post("/manufacturers/add/") # include_in_schema=False исключить из свагера
async def register_user(manufacturer: SManufacturerAdd) -> dict:
    check = await ManufacturerDAO.add(**manufacturer.model_dump())
    if check:
        return {"message": "Manufacturer успешно добавлен!", "manufacturer": manufacturer}
    else:
        return {"message": "Ошибка при добавлении Manufacturer-а!"}

@router.put("/manufacturers/update/")
async def update_major_description(manufacturer: SManufacturerUpdate) -> dict:
    check = await ManufacturerDAO.update(filter_by={'id': manufacturer.id},
                                         manufacturer_name = manufacturer.manufacturer_name,
                                         is_valid=manufacturer.is_valid)
    if check:
        return {"message": "Manufacturer успешно обновлён!", "manufacturer": manufacturer}
    else:
        return {"message": "Ошибка при обновлении описания Manufacturer-а!"}

@router.put("/manufacturers/update/many/", summary="Обновить несколько производителей")
async def update_manufacturers(filters: SManufacturerFilter = Body(..., description="Фильтры для поиска производителей"),
                               updates: SManufacturerUpdate = Body(..., description="Новые значения для обновления")
                               ) -> dict:
    updated_count = await ManufacturerDAO.update_many(filters=filters, values=updates)
    if updated_count == 0:
        raise HTTPException(status_code=404, detail="Нет производителей, соответствующих фильтрам")
    return {
        "message": f"Успешно обновлено {updated_count} производителей",
        "updated_count": updated_count
    }

@router.put("/manufacturers/update_by_id/{id}", response_model=SManufacturer)
async def update_manufacturer(id: int = Path(..., description="ID производителя"),
                              manufacturer_update: SManufacturerUpdateById = Body(..., description="Новые данные для обновления производителя")
                              ) -> dict:
    updated_manufacturer = await ManufacturerDAO.update_one_by_id(data_id=id, values=manufacturer_update)
    if not updated_manufacturer:
        raise HTTPException(status_code=404, detail="Производитель с указанным ID не найден")
    return updated_manufacturer #{"message": "Производитель успешно обновлён!", "manufacturer": updated_manufacturer}


@router.delete("/manufacturers/delete/{manufacturer_id}")
async def delete_manufacturer(manufacturer_id: int) -> dict:
    return await ManufacturerDAO.delete(id=manufacturer_id)
    # check = await ManufacturerDAO.delete(id=manufacturer_id)
    # if check:
    #     return {"message": f"Manufacturer с ID {manufacturer_id} удален!"}
    # else:
    #     return {"message": f"Ошибка при удалении Manufacturer-а! {check}"}




@router.get("/products/", summary="Получить все товары", response_model=List[SProduct])
async def get_all_products(request_body: FiltrProduct = Depends()) -> list[SProduct]:
    return await ProductDAO.find_all_opt(options=[joinedload(Product.manufacturer)],**request_body.to_dict())

@router.get("/products/{id}", summary="Получить один товар по id")
async def get_product_by_filter(request_body: FiltrProduct = Depends()) -> SProduct | dict:
    result = await ProductDAO.find_one_or_none(options=[joinedload(Product.manufacturer)],**request_body.to_dict())
    if result is None:
        return {'message': f'Продукт с указанными вами параметрами не найден!'}
    return result

@router.post("/products/add/")
async def register_user(product: SProductAdd) -> dict:
    check = await ProductDAO.add(**product.model_dump())
    if check:
        return {"message": "Product успешно добавлен!", "product": product}
    else:
        return {"message": "Ошибка при добавлении Product-а!"}



