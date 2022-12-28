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


@pytest.mark.parametrize(
    "username, payload_len, created_at",
    [
        ["frgfm", 12, "2017-04-05T13:34:38Z"],
    ],
)
def test_user_get_info(username, payload_len, created_at):
    user = User(username)
    out = user.get_info()
    assert len(out) == payload_len
    assert out["created_at"] == created_at


@pytest.mark.parametrize(
    "username, expected_error",
    [
        ["imaginary_GH-Friend", HTTPRequestException],
        ["frgfm", None],
    ],
)
def test_user_list_repos(username, expected_error):
    if expected_error is None:
        repos = User(username).list_repos()
        assert isinstance(repos, list) and len(repos) > 1
        assert all(isinstance(elt, str) and len(elt) >= 1 for elt in repos)
    else:
        with pytest.raises(expected_error):
            User(username).list_repos()
