from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.bio_repository import BioRepository
from src.schemas.author_bio import BioCreate, BioResponse
from src.exceptions import NotFoundError
from src.config import get_request_id
import logging

logger = logging.getLogger(__name__)

class BioService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.request_id = get_request_id()
        self.bio_repo = BioRepository(db)

    async def create_bio(self, data: BioCreate) -> BioResponse:
        bio = data.to_model()
        created = await self.bio_repo.create_bio(bio)
        logger.info("Bio created", extra={"author_id": str(created.author_id), "bio_id": str(created.bio_id), "request_id": self.request_id})

        return BioResponse.model_validate(created)

    async def get_bio_by_author_id(self, author_id: UUID) -> BioResponse:
        bio = await self.bio_repo.get_by_author_id(author_id)
        if not bio:
            logger.warning("Bio not found", extra={"author_id": str(author_id), "request_id": self.request_id})
            raise NotFoundError("Bio", f"author_id={author_id}")
        return BioResponse.model_validate(bio)

