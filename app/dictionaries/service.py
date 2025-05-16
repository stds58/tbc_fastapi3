from fastapi import APIRouter, Depends, HTTPException, Body, Path
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from typing import List, Optional
from app.database import async_session_maker
from app.dictionaries.models import Product, Manufacturer, DimensionUnit, Subcategory, Category
from app.dictionaries.services.base import ManufacturerDAO, ProductDAO
from app.dictionaries.schemas import SManufacturer, SManufacturerAdd, SManufacturerUpdate, SManufacturerUpdateById, SManufacturerFilter, SProduct, SProductAdd
from app.dictionaries.filtr import FiltrProduct, FiltrManufacturer
from app.session_maker import get_session_with_isolation
from app.users.router import verify_keycloak_token


async def fetch_all_manufacturers(filters: SManufacturerFilter):
    return await ManufacturerDAO.find_all_opt(options=None, filters=filters)


