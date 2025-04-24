from fastapi import HTTPException, status, Depends
from app.users.models import User
from app.users.auth import get_current_user



async def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав!')


