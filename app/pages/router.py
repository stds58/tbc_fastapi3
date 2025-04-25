from typing import List, Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from app.dictionaries.router import get_all_manufacturers
from app.dictionaries.schemas import SManufacturer, SManufacturerAdd, SManufacturerUpdate, SManufacturerUpdateById, SManufacturerFilter, SProduct, SProductAdd
from app.users.router import register_user, get_me, auth_user
from app.users.schemas import SUserRegister, SUserAuth


# https://habr.com/ru/articles/831386/

router = APIRouter(prefix='/pages', tags=['Фронтенд'])
templates = Jinja2Templates(directory='templates')


@router.get('/manufacturers')
async def get_manufacturers_html(request: Request, manufacturers: List[SManufacturer] = Depends(get_all_manufacturers)):
    # Преобразуем Pydantic-модели в словари с использованием by_alias=True
    manufacturers_data = [manufacturer.model_dump(by_alias=True) for manufacturer in manufacturers]
    return templates.TemplateResponse(
        name='manufacturers.html',
        context={'request': request, 'manufacturers': manufacturers_data}
    )
    #return templates.TemplateResponse(name='manufacturers.html', context={'request': request, 'manufacturers': manufacturers})


@router.get('/register')
async def register(request: Request):
    return templates.TemplateResponse(
        name='registration.html',
        context={'request': request}
    )

@router.get('/login')
async def login(request: Request):
    return templates.TemplateResponse(
        name='login.html',
        context={'request': request}
    )

@router.get('/profile')
async def get_my_profile(request: Request, profile=Depends(get_me)):
    return templates.TemplateResponse(name='profile.html', context={'request': request, 'profile': profile})


