from sqlalchemy import text, ARRAY, String, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base, str_uniq, int_pk
import enum
from typing import List, Optional, Literal
from app.dictionaries.sql_enums import GenderEnum, ProfessionEnum


class User(Base):
    id: Mapped[int_pk]
    phone_number: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str]

    is_user: Mapped[bool] = mapped_column(default=True, server_default=text('true'), nullable=False)
    is_moderator: Mapped[bool] = mapped_column(default=False, server_default=text('false'), nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text('false'), nullable=False)

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"


ProfessionType2 = Literal["MANAGER", "DEVELOPER"]

class Profile(Base):
    id: Mapped[int_pk]
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    age: Mapped[int | None]
    gender: Mapped[GenderEnum] = mapped_column( Enum(GenderEnum, name="genderenum", create_type=False) )
    profession: Mapped[ProfessionEnum] = mapped_column( Enum(ProfessionEnum, name="professionenum", create_type=False),
                                                        default=ProfessionEnum.MANAGER,
                                                        #server_default=text("'MANAGER'")
                                                        server_default = text(f"'{ProfessionEnum.MANAGER.name}'")
                                                        )
    profession2: Mapped[ProfessionType2] = mapped_column(String(50),
                                                         default="MANAGER",
                                                         server_default=text("'MANAGER'")
                                                         )
    profession3: Mapped[ProfessionEnum] = mapped_column(Enum(ProfessionEnum, native_enum=False, length=255),
                                                       default=ProfessionEnum.MANAGER,
                                                       server_default=text(f"'{ProfessionEnum.MANAGER.name}'")
                                                       )
    interests: Mapped[List[str] | None] = mapped_column(ARRAY(String))
    contacts: Mapped[dict | None] = mapped_column(JSON)

# Параметр default:
# Этот параметр задает значение по умолчанию на уровне приложения (SQLAlchemy).
# Это означает, что если при создании объекта в коде значение для данного поля не указано,
# будет использовано значение, указанное в default.
# Например, при создании объекта класса User, если значение для поля profession не передано,
# SQLAlchemy автоматически подставит значение по умолчанию, указанное в default.
# Пример: Если у нас есть перечисление (ENUM) профессий, то значение по умолчанию может быть выбрано через точку,
# например: ProfessionEnum.DEVELOPER.
#
# Параметр server_default:
# Этот параметр задает значение по умолчанию на уровне базы данных.
# Это значит, что если при вставке записи в таблицу значение для данного поля не указано,
# сама база данных подставит значение, указанное в server_default.
# В отличие от default, это значение применяется, если запись добавляется в таблицу напрямую,
# например, через SQL-запросы, минуя приложение.
#
# Важно: Для использования этого параметра с ENUM,
# нужно передавать значение в виде текстового выражения с помощью метода text, который импортируется из SQLAlchemy.
# Значение ENUM указывается в кавычках как текст, например: "WRITER", а не само значение, такое как ProfessionEnum.WRITER.
# Это необходимо для корректного выполнения запроса на стороне базы данных.

# native_enum=False
# Не создает ENUM-тип в базе данных .
# Вместо этого хранит значения перечисления как строки (VARCHAR или TEXT) в базе данных.
# Преобразует значения между строками и объектами Enum на уровне Python.





