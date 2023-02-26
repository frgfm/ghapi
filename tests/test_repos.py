import pytest

from ghapi.connection import Connection
from ghapi.exceptions import HTTPRequestException
from ghapi.repos import Repository


@pytest.mark.parametrize(
    "owner, name, expected_error, expected_repr",
    [
        [None, "ghapi", ValueError, None],
        ["", "ghapi", ValueError, None],
        ["frgfm", None, ValueError, None],
        ["frgfm", "", ValueError, None],
        ["frgfm", "ghapi", None, "Repository(owner='frgfm', name='ghapi')"],
    ],
)
def test_repository_constructor(owner, name, expected_error, expected_repr):
    if expected_error is None:
        repo = Repository(owner, name)
        assert str(repo) == expected_repr
    else:
        with pytest.raises(expected_error):
            Repository(owner, name)


def test_repository_list_pulls(mock_pull):
    conn = Connection(url="https://www.github.com")
    repo = Repository("frgfm", "ghapi", conn)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        repo.list_pulls()
    # Fix url
    repo.conn.url = "https://api.github.com"
    # Set response
    repo._pulls = [mock_pull]
    out = repo.list_pulls()
    assert len(out) == 1 and out[0] == 27


def test_repo_get_info(mock_repo):
    conn = Connection(url="https://www.github.com")
    repo = Repository("frgfm", "ghapi", conn)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        repo.get_info()
    # Fix url
    repo.conn.url = "https://api.github.com"
    # Set response
    repo._info = mock_repo
    out = repo.get_info()
    assert len(out) == 12
    assert out["created_at"] == "2022-12-19T20:52:23Z"


def test_repo_get_content(mock_repo):
    conn = Connection(url="https://www.github.com")
    repo = Repository("frgfm", "ghapi", conn)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        repo.get_content("README.md")
    # Fix url
    repo.conn.url = "https://api.github.com"
    # Set response
    repo._info = mock_repo
    out = repo.get_content("README.md")
    assert isinstance(out, dict) and len(out) == 12


def test_repo_download_archive(mock_repo):
    conn = Connection(url="https://www.github.com")
    repo = Repository("frgfm", "ghapi", conn)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        repo.download_archive("main")
    # Fix url
    repo.conn.url = "https://api.github.com"
    # Set response
    repo._info = mock_repo
    out = repo.download_archive("main")
    assert isinstance(out, str) and out.startswith("https://")
