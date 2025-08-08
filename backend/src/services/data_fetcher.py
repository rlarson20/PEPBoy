# TLDR:
# one function that gets the json data from peps.json
# one function that gets the pep raw data using url

import httpx
# from pprint import pprint as pp

_PEP_URL = "https://peps.python.org/api/peps.json"


def get_pep_json_data():
    return httpx.get(_PEP_URL)


def get_pep_urls(data: "httpx.Response"):
    urls: list[str] = []
    for metadata in data.json().values():
        urls.append(metadata["url"])
    return urls


# I do not like how this is going
# current idea: use a git submodule in order to keep a copy of the data nearby
def get_raw_pep_data(link: str):
    return httpx.get(url=link).read().decode()


# pp(get_raw_pep_data(get_pep_urls(get_pep_json_data())[0]))
