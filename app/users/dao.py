from app.dictionaries.services.base import BaseDAO
from app.users.models import User
from app.users.schemas import SUserRegister


class UsersDAO(BaseDAO):
    model = User
    pydantic_model = SUserRegister

