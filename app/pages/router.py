from typing import List, Optional
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from app.dictionaries.router import get_all_manufacturers
from app.dictionaries.schemas import SManufacturer, SManufacturerAdd, SManufacturerUpdate, SManufacturerUpdateById, SManufacturerFilter, SProduct, SProductAdd



router = APIRouter(prefix='/pages', tags=['Фронтенд'])
templates = Jinja2Templates(directory='templates')


@router.get('/manufacturers')
async def get_manufacturers_html(request: Request,  manufacturers: List[SManufacturer] = Depends(get_all_manufacturers)):
    # Преобразуем Pydantic-модели в словари с использованием by_alias=True
    manufacturers_data = [manufacturer.model_dump(by_alias=True) for manufacturer in manufacturers]
    return templates.TemplateResponse(
        name='manufacturers.html',
        context={'request': request, 'manufacturers': manufacturers_data}
    )
    #return templates.TemplateResponse(name='manufacturers.html', context={'request': request, 'manufacturers': manufacturers})


