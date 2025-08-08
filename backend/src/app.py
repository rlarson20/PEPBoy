from fastapi import FastAPI

app = FastAPI(title="PEPBoy does everything for Python Enhancement Proposals!")


@app.get("/")
def hello_world():
    return {"hello": "world"}


# think this should go in the api folder, not sure how it should get structured tho
# for now, just work with it in here


@app.get("/api/peps")
def get_all_peps():
    pass


@app.get("/api/peps/{pep_number}")
def get_pep_by_number(pep_number: int):
    pass


# initial simple search
@app.get("/api/search")
def search_pep_by_title(q: str):
    pass


# honestly might get shelved soon, FTS comes after v1
# @app.get("/api/fts")
# def full_text_search(q: str):
#     pass
