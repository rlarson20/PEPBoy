# TLDR:
# one function that gets the json data from peps.json
# one function that gets the pep raw data using url

import httpx

from urllib.parse import urlparse
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent  # src/services
_PROJECT_DIR = _SCRIPT_DIR.parent.parent  # backend

_PEP_REPO = Path(str(_PROJECT_DIR) + "/PEP_repo").resolve()
_PEPS_DIR = Path(str(_PEP_REPO) + "/peps").resolve()
_PEP_URL = "https://peps.python.org/api/peps.json"
_INDEX_PEP = "pep-0000.rst"


def get_pep_json_data():
    return httpx.get(_PEP_URL)


def get_pep_files(data: "httpx.Response"):
    """turn the data from the call into list of name files"""
    urls: list[str] = []
    for metadata in data.json().values():
        urls.append(metadata["url"])
    names = [urlparse(u).path.strip("/") + ".rst" for u in urls]
    if _INDEX_PEP in names:
        names.remove(_INDEX_PEP)
    return names


def get_raw_pep_text(pep_name: str):
    """gets the data from the PEP file locally"""
    try:
        with open(str(_PEPS_DIR) + "/" + pep_name, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"


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


def get_name_from_meta(meta: str):
    first_line = meta.split("\n", maxsplit=1)[0]
    return first_line.strip().split(" ", maxsplit=1)[1]


def main():
    # trying to get something working, will be refactored
    raw_data = get_pep_json_data()
    metadata_json = raw_data.json()
    files = get_pep_files(raw_data)
    raw_text = [get_raw_pep_text(file) for file in files]
    for rst in raw_text:
        headers, content = rst.split("\n\n", maxsplit=1)
        content = content.lstrip()
        pep_num = get_name_from_meta(headers)


if __name__ == "__main__":
    main()
