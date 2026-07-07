from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.base import BaseRepository
from src.models.author_bio import AuthorBio

class BioRepository(BaseRepository[AuthorBio]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, AuthorBio)

    async def get_by_author_id(self, author_id: UUID) -> Optional[AuthorBio]:
        query = select(AuthorBio).where(
            AuthorBio.author_id == author_id,
            AuthorBio.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

