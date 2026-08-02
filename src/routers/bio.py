from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.services.bio_service import BioService
from src.schemas.author_bio import BioCreate, BioResponse
from src.exceptions import NotFoundError
from src.db import get_session
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bio", tags=["Bio"])

async def get_bio_service(db: AsyncSession = Depends(get_session)) -> BioService:
    return BioService(db)

@router.post(
    "/",
    response_model=BioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create bio",
    description="Create bio for author",
)
async def create_bio(data: BioCreate, service: BioService = Depends(get_bio_service)):
    try:
        return await service.create_bio(data)
    except Exception as e:
        logger.error(f"Failed to create bio: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to create bio: {str(e)}")

@router.get(
    "/{author_id}",
    response_model=BioResponse,
    summary="Get bio",
    description="Get bio for author_id"
)
async def get_bio_by_author_id(author_id: UUID, service: BioService = Depends(get_bio_service)):
    try:
        return await service.get_bio_by_author_id(author_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error(f"Failed to get bio: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get bio: {str(e)}")


