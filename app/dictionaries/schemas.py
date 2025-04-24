#модели Pydantic
from datetime import datetime, date
from typing import Optional, List
import re
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator




class BaseFilter(BaseModel):
    class Config:
        extra = "forbid"  # Запрещаем передачу лишних полей


class SManufacturer(BaseModel):
    """from_attributes = True: позволяет модели автоматически маппить атрибуты Python объектов на поля модели.
                               Примерно то что мы делали в методе to_dict, но более расширенно.
       use_enum_values = True: это указание преобразовывать значения перечислений в их фактические значения,
                               а не в объекты перечислений. Просто для удобства восприятия человеком."""
    model_config = ConfigDict(from_attributes=True, max_recursion_depth=1)
    id: int
    manufacturer_name: str = Field(..., description="производитель")
    is_valid: bool = Field(..., description="производитель работает")
    #product: List[Optional['SProduct']] = Field(None, description="вложенная схема Product")

    # @field_validator("phone_number")
    # def validate_phone_number(cls, value):
    #     if not re.match(r'^\d{2,3}$', value):
    #         raise ValueError('производитель должен содержать от 2 до 3 цифр')
    #     return value

    # @field_validator("date_of_birth")
    # def validate_date_of_birth(cls, value):
    #     if value and value >= datetime.now().date():
    #         raise ValueError('Дата рождения должна быть в прошлом')
    #     return value


class SManufacturerAdd(BaseModel):
    manufacturer_name: str = Field(..., description="производитель")
    is_valid: bool = Field(..., description="производитель работает")


class SManufacturerUpdate(BaseModel):
    manufacturer_name: Optional[str] = None
    is_valid: Optional[bool] = None


class SManufacturerUpdateById(BaseModel):
    manufacturer_name: str = Field(..., description="производитель")
    is_valid: bool = Field(..., description="производитель работает")

class SManufacturerFilter(BaseFilter):
    id: Optional[int] = None
    manufacturer_name: Optional[str] = None
    is_valid: Optional[bool] = None



class SProduct(BaseModel):
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


class SProductAdd(BaseModel):
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