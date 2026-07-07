from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.bio_repository import BioRepository
from src.schemas.author_bio import BioCreate, BioResponse
from src.exceptions import NotFoundError
from src.middleware.request_id import get_request_id
from src.services.base import BaseService
import logging

logger = logging.getLogger(__name__)

class BioService(BaseService):
    def __init__(self, db: AsyncSession):
        self.db = db
        self.request_id = get_request_id()
        self.bio_repo = BioRepository(db)

    async def create_bio(self, data: BioCreate) -> BioResponse:
        self._log_info("Creating bio for author", author_id=str(data.author_id), request_id=self.request_id)

        bio = await self.bio_repo.create(**data.model_dump())
        await self.db.refresh(bio)

        return BioResponse.model_validate(bio)

    async def get_bio_by_author_id(self, author_id: UUID) -> BioResponse:
        self._log_info("Fetching bio by author_id", author_id=str(author_id), request_id=self.request_id)
        bio = await self.bio_repo.get_by_author_id(author_id)
        if not bio:
            self._log_warning("Bio not found for author", author_id=str(author_id), request_id=self.request_id)
            raise NotFoundError("Bio", f"author_id={author_id}")
        return BioResponse.model_validate(bio)

