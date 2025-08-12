# TODO: use the `services/data_fetcher.py` to populate database

from .services.data_fetcher import get_pep_json_data


def populate_database():
    metadata = get_pep_json_data.json()

    for pep_number, pep_data in metadata_json.items():
        pass
        # make pep objects
        # create/update DB records
        # handle author stuff


"""done when: db has all peps from repo, API endpoints return actual data, populate_database is idempotent"""
