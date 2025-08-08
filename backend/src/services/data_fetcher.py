# TLDR:
# one function that gets the json data from peps.json
# one function that gets the pep raw data using url

import httpx

# from pprint import pprint as pp
from urllib.parse import urlparse
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent  # src/services
_PROJECT_DIR = _SCRIPT_DIR.parent.parent  # backend

_PEP_REPO = Path(str(_PROJECT_DIR) + "/PEP_repo")
_PEPS_DIR = Path(str(_PEP_REPO) + "/peps")
_PEP_URL = "https://peps.python.org/api/peps.json"
_INDEX_PEP = "pep-0000.rst"


def get_pep_json_data():
    return httpx.get(_PEP_URL)


def get_pep_files(data: "httpx.Response"):
    urls: list[str] = []
    for metadata in data.json().values():
        urls.append(metadata["url"])
    # TODO: check for 0000 because that's the index and doesn't exist in the repo, can redirect to our index
    names = [urlparse(u).path.strip("/") + ".rst" for u in urls]
    if _INDEX_PEP in names:
        names.remove(_INDEX_PEP)
    return names


def get_raw_pep_text(pep_name: str):
    try:
        print(_PEPS_DIR)
        with open(str(_PEPS_DIR) + "/" + pep_name + ".rst", "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error: {e}")


# pp(get_raw_pep_data(get_pep_urls(get_pep_json_data())[0]))
# pp(get_pep_files(get_pep_json_data()))


def test_if_peps_have_been_updated():
    succ = 0
    fail = 0
    total = 0
    test_data = get_pep_files(get_pep_json_data())
    for file in [str(_PEPS_DIR) + "/" + n for n in test_data]:
        try:
            with open(file, "r") as f:
                print("Success!")
                succ += 1
        except Exception as e:
            print(f"Failure: {e}")
            fail += 1
        finally:
            total += 1

    print(f"Succeeded: {succ}\nFailed: {fail}\nTotal: {total}")


print(get_raw_pep_text("pep-0008"))
