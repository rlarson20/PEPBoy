from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .models.database import get_db
from .models.pydantic_models import PEPResponse, PEPListResponse
from .services.pep_repository import PEPRepository

app = FastAPI(title="PEPBoy does everything for Python Enhancement Proposals!")


@app.get("/")
def hello_world():
    return {"hello": "world"}


# think this should go in the api folder, not sure how it should get structured tho
# for now, just work with it in here


@app.get("/api/peps", response_model=PEPListResponse)
def get_all_peps(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = PEPRepository(db)
    peps = repo.list_all_peps(skip=skip, limit=limit)
    total = repo.get_peps_count()
    return PEPListResponse(
        peps=[PEPResponse.from_orm(pep) for pep in peps],
        total=total,
        skip=skip,
        limit=limit
    )


@app.get("/api/peps/{pep_number}", response_model=PEPResponse)
def get_pep_by_number(pep_number: int, db: Session = Depends(get_db)):
    repo = PEPRepository(db)
    pep = repo.get_pep_by_number(pep_number)
    if not pep:
        raise HTTPException(status_code=404, detail="PEP not found")
    return PEPResponse.from_orm(pep)


# initial simple search
@app.get("/api/search")
def search_pep_by_title(q: str, db: Session = Depends(get_db)):
    repo = PEPRepository(db)
    peps = repo.search_peps_by_title(q)
    return PEPListResponse(
        peps=[PEPResponse.from_orm(pep) for pep in peps],
        total=len(peps),
        skip=0,
        limit=len(peps)
    )


# honestly might get shelved soon, FTS comes after v1
# @app.get("/api/fts")
# def full_text_search(q: str):
#     pass
