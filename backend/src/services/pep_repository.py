from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional

from ..models.orm_models import PEP, Author

class PEPRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_pep_by_number(self, pep_number: int) -> Optional[PEP]:
        """Get a single PEP by its number."""
        return self.db.execute(
            select(PEP).where(PEP.number == pep_number)
        ).scalar_one_or_none()
    
    def list_all_peps(self, skip: int = 0, limit: int = 100) -> List[PEP]:
        """Get all PEPs with pagination."""
        return self.db.execute(
            select(PEP).offset(skip).limit(limit)
        ).scalars().all()
    
    def search_peps_by_title(self, query: str) -> List[PEP]:
        """Simple title search (foundation for future FTS)."""
        return self.db.execute(
            select(PEP).where(PEP.title.ilike(f"%{query}%"))
        ).scalars().all()
    
    def get_peps_count(self) -> int:
        """Get total number of PEPs."""
        return self.db.execute(select(func.count(PEP.number))).scalar()