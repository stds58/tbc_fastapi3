from typing import List, Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.dictionaries.router import get_all_manufacturers
from app.dictionaries.schemas import SManufacturer, SManufacturerAdd, SManufacturerUpdate, SManufacturerUpdateById, SManufacturerFilter, SProduct, SProductAdd
from app.users.router import register_user, get_me , get_current_user, verify_keycloak_token #, auth_user, login_oauth
from app.users.schemas import SUserRegister, SUserAuth
from pathlib import Path
from app.dictionaries.service import fetch_all_manufacturers


# https://habr.com/ru/articles/831386/

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = Path(__file__).parent.parent
router = APIRouter(prefix='/pages', tags=['Фронтенд'])
templates = Jinja2Templates(directory=PROJECT_DIR / "templates")
# Получаем список путей, где ищутся шаблоны
searchpath = templates.env.loader.searchpath
# Если нужно как строку (например, первый путь)
#print("Search path:", searchpath[0])

@router.get('/list-templates')
def list_templates(request: Request):
    template_names = templates.env.list_templates()
    print('template_names ',template_names)
    return {"available_templates": template_names}

@router.get("/protected", response_class=HTMLResponse)
async def protected_page(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})


@router.get('/manufacturers', response_class=HTMLResponse)
async def get_manufacturers_html(
        request: Request,
        user: dict = Depends(verify_keycloak_token)
    ):
    print('user11111   ',user)
    # Преобразуем Pydantic-модели в словари с использованием by_alias=True
    manufacturers = await fetch_all_manufacturers(SManufacturerFilter())
    #manufacturers_data = [manufacturer.model_dump(by_alias=True) for manufacturer in manufacturers]
    print('dddddddddd')
    return templates.TemplateResponse(
        name='manufacturers.html',
        context={'request': request, 'manufacturers': manufacturers}
    )


@router.get('/register')
async def register(request: Request):
    return templates.TemplateResponse(
        name='registration.html',
        context={'request': request}
    )

# @router.get('/login_oauth')
# async def login(request: Request):
#     return templates.TemplateResponse(
#         name='login_oauth.html',
#         context={'request': request}
#     )

@router.get("/login")
async def login_oauth_page(request: Request):
    return templates.TemplateResponse("login_oauth.html", {"request": request})

# @router.get('/profile')
# async def get_my_profile(request: Request, profile=Depends(get_me)):
#     return templates.TemplateResponse(name='profile.html', context={'request': request, 'profile': profile})

@router.get("/profile")
async def profile_page(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(name="profile.html", context={"request": request, "user": user})


