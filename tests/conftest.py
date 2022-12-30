import json
import os

import pytest


@pytest.fixture(scope="session")
def mock_repo():
    with open(os.path.join("tests", "fixtures", "repo.json"), "rb") as f:
        response = json.load(f)
    return response


@pytest.fixture(scope="session")
def mock_pull():
    with open(os.path.join("tests", "fixtures", "pull.json"), "rb") as f:
        response = json.load(f)
    return response
