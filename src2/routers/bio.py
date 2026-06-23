from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from src2.services.bio_service import BioService
from src2.schemas.author_bio import BioCreate, BioResponse
from src2.db import get_session
from src2.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/bio", tags=["Bio"])

@router.post("/", response_model=BioResponse, status_code=status.HTTP_201_CREATED)
async def create_bio(data: BioCreate, db: AsyncSession = Depends(get_session)):
    service = BioService(db)
    return await service.create_bio(data)

@router.get("/{author_id}", response_model=BioResponse)
async def get_bio_by_author_id(author_id: UUID, db: AsyncSession = Depends(get_session)):
    service = BioService(db)
    return await service.get_bio_by_author_id(author_id)

