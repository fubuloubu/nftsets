from pathlib import Path

import pytest

DATA_FOLDER = Path(__file__).parent / "data"
COLLECTIONS = DATA_FOLDER / "collections"


@pytest.fixture(params=[str(path) for path in COLLECTIONS.glob("*.json")])
def raw_collection_file(request):
    return request.param
