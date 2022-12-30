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


@pytest.fixture(scope="session")
def mock_pull_diff():
    with open(os.path.join("tests", "fixtures", "pull_diff.json"), "rb") as f:
        response = json.load(f)
    return response


@pytest.fixture(scope="session")
def mock_review():
    with open(os.path.join("tests", "fixtures", "review.json"), "rb") as f:
        response = json.load(f)
    return response


@pytest.fixture(scope="session")
def mock_comment():
    with open(os.path.join("tests", "fixtures", "comment.json"), "rb") as f:
        response = json.load(f)
    return response


@pytest.fixture(scope="session")
def mock_user():
    with open(os.path.join("tests", "fixtures", "user.json"), "rb") as f:
        response = json.load(f)
    return response
