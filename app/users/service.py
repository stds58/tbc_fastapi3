
from app.users.auth import get_password_hash, create_access_token, authenticate_user, get_current_user
from app.users.dao import UsersDAO
from app.users.schemas import SUserRegister, SUserAuth
from app.users.exceptions import UserAlreadyExistsError, IncorrectEmailOrPasswordException

class UserService:
    @classmethod
    async def register_user(cls, user_data: SUserRegister) -> dict:
        user = await UsersDAO.find_one_or_none(options=None, filters={"email": user_data.email})
        if user:
            raise UserAlreadyExistsError()

        # hashed_password =get_password_hash(user_data.password)
        # await UsersDAO.add(
        #     email=user_data.email,
        #     password=hashed_password,
        #     #другие поля
        # )
        user_dict = user_data.model_dump()
        hashed_password = get_password_hash(user_data.password)
        user_dict['password'] = hashed_password
        await UsersDAO.add(**user_dict)
        return {'message': 'Вы успешно зарегистрированы!'}


