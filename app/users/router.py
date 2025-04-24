from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import Response
from app.exceptions import IncorrectEmailOrPasswordException
from app.users.auth import get_password_hash, create_access_token, authenticate_user, get_current_user
from app.users.dao import UsersDAO
from app.users.models import User
from app.users.schemas import SUserRegister, SUserAuth
from app.users.dependencies import get_current_admin_user



router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post("/register/")
async def register_user(user_data: SUserRegister) -> dict:
    user = await UsersDAO.find_one_or_none(options=None,filters={"email": user_data.email})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )
    user_dict = user_data.model_dump()
    user_dict['password'] = get_password_hash(user_data.password)
    await UsersDAO.add(**user_dict)
    return {'message': 'Вы успешно зарегистрированы!'}


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

@router.post("/login/")
async def auth_user(response: Response, user_data: SUserAuth):
    check = await authenticate_user(email=user_data.email, password=user_data.password)
    if check is None:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'ok': True, 'access_token': access_token, 'refresh_token': None, 'message': 'Авторизация успешна!'}





@router.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}


@router.get("/me/")
async def get_me(user_data: User = Depends(get_current_user)):
    return user_data


@router.get("/all_users/")
async def get_all_users(user_data: User = Depends(get_current_admin_user)):
    return await UsersDAO.find_all()


