from sqlalchemy import ForeignKey, text, Text, UniqueConstraint, Index, func, CheckConstraint, column
from sqlalchemy.orm import relationship, Mapped, mapped_column, backref
from typing import List, Optional
from sqlalchemy import String, Boolean
from app.database import (Base, str_uniq, int_pk, str_null_true, created_at, updated_at,
                          bool_null_false, fk_protect_nullable)


class Product(Base):
    id: Mapped[int_pk]
    product_name: Mapped[str_null_true] = mapped_column(info={"verbose_name": "наименование"})
    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("manufacturer.id", ondelete="RESTRICT"), nullable=True, info={"verbose_name": "производитель"})
    artikul: Mapped[str_null_true] = mapped_column(info={"verbose_name": "артикул"})
    subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategory.id", ondelete="RESTRICT"), nullable=True, info={"verbose_name": "подкатегория"})
    dimension_id: Mapped[int] = mapped_column(ForeignKey("dimensionunit.id", ondelete="RESTRICT"), nullable=True, info={"verbose_name": "ед изм"})
    comment_text: Mapped[str_null_true] = mapped_column(info={"verbose_name": "комментарий"})
    #creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"), ondelete="RESTRICT", nullable=False, info={"verbose_name": "инициатор"})
    date_create: Mapped[created_at] = mapped_column(info={"verbose_name": "дата создания"})
    is_moderated: Mapped[bool_null_false] = mapped_column(info={"verbose_name": "изменено"})
    #moderated_by: Mapped[int] = mapped_column(ForeignKey("user.id"), ondelete="RESTRICT", nullable=False, info={"verbose_name": "модератор"})
    date_moderated: Mapped[updated_at] = mapped_column(info={"verbose_name": "дата изменения"})
    name_full: Mapped[str_null_true] = mapped_column(info={"verbose_name": "полное наименование"})
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product.id"),nullable=True, info={"verbose_name": "псевдоним"})

    # Обратная связь (related_name аналог)
    manufacturer: Mapped["Manufacturer"] = relationship("Manufacturer", back_populates="product")
    subcategory: Mapped["Subcategory"] = relationship("Subcategory", back_populates="product")
    dimension: Mapped["DimensionUnit"] = relationship("DimensionUnit", back_populates="product")
    children = relationship("Product")
    #creator: Mapped["User"] = relationship("User", back_populates="product")
    #moderated_by: Mapped["User"] = relationship("User", back_populates="product")

    __table_args__ = (
        Index(
            'uix_product_unique',
            func.lower("product_name"),
            "manufacturer_id",
            func.lower("artikul"),
            "dimension_id",
            unique=True
        ),
        CheckConstraint("access_id > 0", name="access_id_positive_number_check"),
        Index("product_name_idx", func.lower("product_name")),
        Index("artikul_idx", func.lower("artikul")),
        Index("name_full_idx", func.lower("name_full")),
    )

    def __repr__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"name_full={self.name_full!r})")

    def to_dict(self) -> dict:
        return {'id': self.id,
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


class Manufacturer(Base):
    id: Mapped[int_pk]
    manufacturer_name: Mapped[str] = mapped_column(info={"verbose_name": "производитель"})
    is_valid: Mapped[bool_null_false] = mapped_column(info={"verbose_name": "производитель работает"})

    product: Mapped[List["Product"]] = relationship("Product", back_populates="manufacturer")

    __table_args__ = (
        Index('uix_manufacturer_name_lower', func.lower(column('manufacturer_name')), unique=True),
        CheckConstraint("access_id > 0", name="access_id_positive_number_check"),
    )

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"manufacturer_name={self.manufacturer_name!r})")

    def __repr__(self):
        return str(self)

    def to_dict(self) -> dict:
        return {'id': self.id,
                'manufacturer_name': self.manufacturer_name,
                'is_valid': self.is_valid
                }


class DimensionUnit(Base):
    id: Mapped[int_pk]
    dimension_name: Mapped[str_uniq] = mapped_column(info={"verbose_name": "наименование"})
    dimension_code: Mapped[str_null_true] = mapped_column(info={"verbose_name": "код"})

    product: Mapped[List["Product"]] = relationship("Product", back_populates="dimension")

    __table_args__ = (
        Index('uix_dimension_name_lower', func.lower("dimension_name"), unique=True),
        Index('uix_dimension_code_lower', func.lower("dimension_code"), unique=True),
        CheckConstraint("access_id > 0", name="access_id_positive_number_check"),
    )

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"dimension_code={self.dimension_code!r}, "
                f"dimension_name={self.dimension_name!r})")

    def __repr__(self):
        return str(self)


class Subcategory(Base):
    id: Mapped[int_pk]
    subcategory_name: Mapped[str_uniq] = mapped_column(info={"verbose_name": "подкатегория"})
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id", ondelete="RESTRICT"), nullable=False,info={"verbose_name": "категория"})
    control: Mapped[int] = mapped_column(info={"verbose_name": "контроль"})

    category: Mapped["Category"] = relationship("Category", back_populates="subcategory")
    product: Mapped[List["Product"]] = relationship("Product", back_populates="subcategory")

    __table_args__ = (
        Index('uix_subcategory_name_lower', func.lower("subcategory_name"), unique=True),
        CheckConstraint("access_id > 0", name="access_id_positive_number_check"),
    )

    def __repr__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"subcategory_name={self.subcategory_name!r})")


class Category(Base):
    id: Mapped[int_pk]
    category_name: Mapped[str_uniq] = mapped_column(info={"verbose_name": "категория"})

    subcategory: Mapped[List["Subcategory"]] = relationship("Subcategory", back_populates="category")

    __table_args__ = (
        Index('uix_category_name_lower', func.lower("category_name"), unique=True),
        CheckConstraint("access_id > 0", name="access_id_positive_number_check"),
    )

    def __repr__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"category_name={self.category_name!r})")






