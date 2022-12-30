import pytest

from ghapi.connection import Connection
from ghapi.exceptions import HTTPRequestException
from ghapi.users import User


@pytest.mark.parametrize(
    "username, expected_error",
    [
        ["", ValueError],
        [42, ValueError],
        ["frgfm", None],
    ],
)
def test_user_constructor(username, expected_error):
    if expected_error is None:
        user = User(username)
        assert isinstance(user.conn, Connection)
    else:
        with pytest.raises(expected_error):
            User(username)


def test_user_get_info(mock_user):
    conn = Connection(url="https://www.github.com")
    user = User("frgfm", conn)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        user.get_info()
    # Fix url
    user.conn.url = "https://api.github.com"
    # Set response
    user._info = mock_user
    out = user.get_info()
    assert len(out) == 12
    assert out["created_at"] == "2017-04-05T13:34:38Z"


def test_user_list_repos(mock_repo):
    conn = Connection(url="https://www.github.com")
    user = User("frgfm", conn)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        user.list_repos()
    # Fix url
    user.conn.url = "https://api.github.com"
    # Set response
    user._repos = [mock_repo]
    out = user.list_repos()
    assert len(out) == 1 and out[0] == "frgfm/ghapi"
