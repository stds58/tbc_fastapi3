from sqlalchemy import text, ARRAY, String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base, str_uniq, int_pk
import enum
from typing import List, Optional


# Enum из модуля enum в Python используется для создания перечислений, которые представляют собой набор именованных значений.
# Это позволяет определять типы данных с ограниченным набором возможных значений


class GenderEnum(str, enum.Enum):
    MALE = "мужчина"
    FEMALE = "женщина"

class ProfessionEnum(str, enum.Enum):
    DEVELOPER = "разработчик"
    DESIGNER = "дизайнер"
    MANAGER = "менеджер"





