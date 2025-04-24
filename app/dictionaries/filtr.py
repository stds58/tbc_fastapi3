#классы, описывающие тело запроса
from datetime import datetime


class FiltrProduct:
    def __init__(self,
                 product_id: int | None = None,
                 product_name: str | None = None,
                 manufacturer_id: int | None = None,
                 artikul: str | None = None,
                 subcategory_id: int | None = None,
                 dimension_id: int | None = None,
                 comment_text: str | None = None,
                 date_create: datetime | None = None,
                 is_moderated: bool | None = None,
                 date_moderated: datetime | None = None,
                 name_full: str | None = None,
                 parent_id: int | None = None
                 ):
        self.id = product_id
        self.product_name = product_name
        self.manufacturer_id = manufacturer_id
        self.artikul = artikul
        self.subcategory_id = subcategory_id
        self.dimension_id = dimension_id
        self.comment_text = comment_text
        self.date_create = date_create
        self.is_moderated = is_moderated
        self.date_moderated = date_moderated
        self.name_full = name_full
        self.parent_id = parent_id

    def to_dict(self) -> dict:
        data = {'id': self.id,
                'product_name': self.product_name,
                'manufacturer_id': self.manufacturer_id,
                'artikul': self.artikul,
                'subcategory_id': self.subcategory_id,
                'dimension_id': self.dimension_id,
                'comment_text': self.comment_text,
                'date_create': self.date_create,
                'is_moderated': self.is_moderated,
                'date_moderated': self.date_moderated,
                'name_full': self.name_full,
                'parent_id': self.parent_id
                }
        # Создаем копию словаря, чтобы избежать изменения словаря во время итерации
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data


class FiltrManufacturer:
    def __init__(self,
                 manufacturer_id: int | None = None,
                 manufacturer_name: str | None = None,
                 is_valid: bool | None = None):
        self.id = manufacturer_id
        self.manufacturer_name = manufacturer_name
        self.is_valid =is_valid

    def to_dict(self) -> dict:
        data = {'id': self.id,
                'manufacturer_name': self.manufacturer_name,
                'is_valid': self.is_valid
                }
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data



