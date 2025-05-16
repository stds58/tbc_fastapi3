from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import Response
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from app.exceptions import IncorrectEmailOrPasswordException
from app.users.auth import get_password_hash, create_access_token, authenticate_user, get_current_user
from app.users.dao import UsersDAO
from app.users.models import User
from app.users.schemas import SUserRegister, SUserAuth
from app.users.dependencies import get_current_admin_user
from app.users.service import UserService
from app.config import settings
from urllib.parse import quote_plus
import os
import requests
import json
import httpx



router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post("/register-local/")
async def register_user(user_data: SUserRegister) -> dict:
    return await UserService.register_user(user_data)



# @router.get("/manufacturers/{id}", summary="Получить одого производителя")
# async def get_manufacturer_by_filter(request_body: SManufacturerFilter = Depends()) -> SManufacturer | dict:
#     result = await ManufacturerDAO.find_one_or_none(options=None,filters=request_body)
#     if result is None:
#         return {'message': f'Производитель с указанными вами параметрами не найден!'}
#     return result



@router.post("/login2/")
async def auth_user(response: Response, user_data: SUserAuth):
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    access_token = create_access_token({"sub": str(check.id)})
    #Если данные о пользователе получены, то мы генерируем JWT токен, а затем записываем его в куку.
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    # Флаг httponly=True, установленный при установке куки с помощью метода response.set_cookie, указывает браузеру,
    # что куки должны быть доступны только через HTTP или HTTPS, и не могут быть доступны скриптам JavaScript на стороне клиента.
    # Это повышает безопасность приложения, так как куки, содержащие чувствительные данные,
    # такие как токены аутентификации (access_token), не могут быть скомпрометированы через атаки XSS (межсайтовый скриптинг).
    # Таким образом, флаг httponly=True помогает защитить данные пользователя от несанкционированного доступа и использования.
    return {'access_token': access_token, 'refresh_token': None}

@router.post("/login-local/")
async def auth_user(response: Response, user_data: SUserAuth):
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    if check is None:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'ok': True, 'access_token': access_token, 'refresh_token': None, 'message': 'Авторизация успешна!'}


oauth = OAuth()

oauth.register(
    name='keycloak',
    client_id=settings.KEYCLOAK_CLIENT_ID,
    client_secret=settings.KEYCLOAK_CLIENT_SECRET,
    server_metadata_url=f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/.well-known/openid-configuration",
    redirect_uri=f"{settings.FRONT_URL}/auth/callback/",
    client_kwargs={'scope': 'openid profile email'}
)
# Настройка Keycloak
KEYCLOAK_URL = settings.KEYCLOAK_URL
KEYCLOAK_REALM = settings.KEYCLOAK_REALM
KEYCLOAK_CLIENT_ID = settings.KEYCLOAK_CLIENT_ID
KEYCLOAK_CLIENT_SECRET = settings.KEYCLOAK_CLIENT_SECRET # удалить, если Access Type = public
KEYCLOAK_ADMIN = settings.KEYCLOAK_ADMIN
KEYCLOAK_ADMIN_PASSWORD = settings.KEYCLOAK_ADMIN_PASSWORD
MASTER_REALM = "master"


@router.get("/login/")
async def login_oauth(request: Request):
    print('2222222222222222')
    redirect_uri = request.url_for("auth_callback")
    try:
        return await oauth.keycloak.authorize_redirect(request, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка OAuth: {e}")

@router.get("/callback/")
async def auth_callback(request: Request):
    try:
        token = await oauth.keycloak.authorize_access_token(request)
        user_info = token.get('userinfo')  # данные пользователя из Keycloak
        access_token = token['access_token']
        request.session["user"] = dict(user_info)
        request.session["access_token"] = access_token

        # Восстанавливаем URL, откуда пришёл пользователь
        next_url = request.session.pop("redirect_after_login", "/")
        # Создаем ответ и устанавливаем куки
        response = RedirectResponse(url=next_url)
        response.set_cookie(key="users_access_token", value=access_token, httponly=True, path="/")
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка аутентификации: {e}")
        #raise HTTPException(status_code=400, detail=f"Ошибка авторизации: {e}")
        #return {"error": str(e)}


@router.post("/logout-local/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}

@router.get("/logout/")
async def logout_user(request: Request, response: Response):
    response.delete_cookie("users_access_token")
    request.session.clear()
    post_logout_redirect_uri = f"{settings.FRONT_URL}/pages/login"
    keycloak_logout_url = (
        f"{settings.KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout?"
        f"post_logout_redirect_uri={post_logout_redirect_uri}&client_id={KEYCLOAK_CLIENT_ID}"
    )
    return RedirectResponse(url=keycloak_logout_url)


async def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        # Сохраняем текущий URL для редиректа после логина
        request.session["redirect_after_login"] = str(request.url)
        raise HTTPException(status_code=307, detail="Redirect to login", headers={"Location": "/pages/login"})
    return user

async def verify_keycloak_token(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        # Нет токена → редирект на логин
        request.session["redirect_after_login"] = str(request.url)
        raise HTTPException(
            status_code=307,
            detail="Missing token",
            headers={"Location": "/pages/login"}
        )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8080/realms/tbcrealm/protocol/openid-connect/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        #print('access_token ',access_token)
        #print('response ',response)
        if response.status_code != 200:
            # Токен недействителен → очищаем сессию и редиректим
            request.session.clear()
            request.session["redirect_after_login"] = str(request.url)
            raise HTTPException(
                status_code=307,
                detail="Token invalid or expired",
                headers={"Location": "/pages/login"}
            )

        user_info = response.json()
        request.session["user"] = user_info  # Обновляем данные пользователя
        return user_info


@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)):
    return user_data


@router.get("/all_users/")
async def get_all_users(user_data: User = Depends(get_current_admin_user)):
    return await UsersDAO.find_all()


@router.get("/test-session")
async def test_session(request: Request):
    request.session["test"] = "session_data"
    return {"session": request.session}

