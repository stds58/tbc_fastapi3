#модели Pydantic  https://habr.com/ru/companies/amvera/articles/851642/
from datetime import datetime, date
from typing import Optional, List
import re
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator, model_validator, computed_field




class BaseConfigModel(BaseModel):
    """https://docs.pydantic.dev/latest/api/config/"""
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Удалять начальные и конечные пробелы для типов str
        from_attributes=True,       # Разрешить работу с ORM-объектами
        populate_by_name=True,      # Разрешить использование алиасов
        use_enum_values=True,       # Использовать значения ENUM вместо объектов
        extra="ignore",             # Игнорировать лишние поля
        max_recursion_depth=1,
    )

class BaseFilter(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"  # Запретить передачу лишних полей
    )


class SManufacturer(BaseConfigModel):
    id: int
    manufacturer_name: str = Field(..., description="производитель",alias="manufacturer_name_alias")
    is_valid: bool = Field(..., description="производитель работает", exclude=True) # exclude=True Исключение полей из сериализации
    #product: List[Optional['SProduct']] = Field(None, description="вложенная схема Product")

    @computed_field
    def full_name(self) -> str:
        return f"{self.manufacturer_name} - {self.is_valid}"


class SManufacturerAdd(BaseConfigModel):
    manufacturer_name: str = Field(..., description="производитель")
    is_valid: bool = Field(..., description="производитель работает")


class SManufacturerUpdate(BaseConfigModel):
    manufacturer_name: Optional[str] = None
    is_valid: Optional[bool] = None


class SManufacturerUpdateById(BaseConfigModel):
    manufacturer_name: str = Field(..., description="производитель")
    is_valid: bool = Field(..., description="производитель работает")

class SManufacturerFilter(BaseFilter):
    id: Optional[int] = None
    manufacturer_name: Optional[str] = None
    is_valid: Optional[bool] = None



class SProduct(BaseConfigModel):
    model_config = ConfigDict(from_attributes=True, max_recursion_depth=1)
    id: int
    product_name: str = Field(..., description="наименование")
    manufacturer_id: Optional[int] = Field(None, ge=1, description="производитель")
    manufacturer: Optional['SManufacturer'] = Field(None, description="вложенная схема производителя")
    artikul: Optional[str] = Field(None, description="артикул")
    subcategory_id: Optional[int] = Field(None, ge=1, description="подкатегория")
    dimension_id: Optional[int] = Field(None, ge=1, description="ед изм")
    comment_text: Optional[str] = Field(None, description="комментарий")
    date_create: datetime = Field(..., description="дата создания")
    is_moderated: bool = Field(..., description="изменено")
    date_moderated: datetime = Field(..., description="дата изменения")
    name_full: Optional[str] = Field(None, description="полное наименование")
    parent_id: Optional[int] = Field(None, ge=1, description="псевдоним")


class SProductAdd(BaseConfigModel):
    product_name: str = Field(..., description="наименование")
    manufacturer_id: Optional[int] = Field(None, ge=1, description="производитель")
    artikul: Optional[str] = Field(None, description="артикул")
    subcategory_id: Optional[int] = Field(None, ge=1, description="подкатегория")
    dimension_id: Optional[int] = Field(None, ge=1, description="ед изм")
    comment_text: Optional[str] = Field(None, description="комментарий")
    is_moderated: bool = Field(..., description="изменено")
    name_full: Optional[str] = Field(None, description="полное наименование")
    parent_id: Optional[int] = Field(None, ge=1, description="псевдоним")


class SProductFilter(BaseFilter):
    id: Optional[int] = None
    product_name: Optional[str] = None
    manufacturer_id: Optional[int] = None
    artikul: Optional[str] = None
    subcategory_id: Optional[int] = None
    dimension_id: Optional[int] = None
    comment_text: Optional[str] = None
    #date_create: datetime | None = None,
    is_moderated: Optional[bool] = None
    #date_moderated: datetime | None = None,
    name_full: Optional[str] = None
    parent_id: Optional[int] = None




    # @field_validator("phone_number", mode='before')
    # def validate_phone_number(cls, value):
    #     if not re.match(r'^\d{2,3}$', value):
    #         raise ValueError('производитель должен содержать от 2 до 3 цифр')
    #     return value

    # @field_validator("date_of_birth", mode='before')
    # def validate_date_of_birth(cls, value):
    #     if value and value >= datetime.now().date():
    #         raise ValueError('Дата рождения должна быть в прошлом')
    #     return value

    # @model_validator(mode='after')
    # def check_age(self):
    #     today = date.today()
    #     age = today.year - self.birthday_date.year - (
    #             (today.month, today.day) < (self.birthday_date.month, self.birthday_date.day))
    #
    #     if age < 18:
    #         raise ValueError("Пользователь должен быть старше 18 лет")
    #     if age > 120:
    #         raise ValueError("Возраст не может превышать 120 лет")
    #     return self
    #
    # @model_validator(mode='after')
    # def set_default_name(self):
    #     if self.name.strip() == '':
    #         self.name = f"User_{self.id}"
    #     return self

