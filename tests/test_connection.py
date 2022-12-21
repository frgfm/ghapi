import pytest
from requests.exceptions import ConnectionError, MissingSchema

from ghapi.connection import Connection


@pytest.mark.parametrize(
    "token, url, expected_error, expected_repr",
    [
        [None, "hello", MissingSchema, ""],
        [None, "https://imaginary.website.dev", ConnectionError, ""],
        [None, "https://api.github.com", None, "Connection(url='https://api.github.com')"],
        ["DUMMY_TOKEN", "https://api.github.com", None, "Connection(url='https://api.github.com')"],
    ],
)
def test_connection_repr(token, url, expected_error, expected_repr):
    if expected_error is None:
        conn = Connection(token, url)
        assert str(conn) == expected_repr
    else:
        with pytest.raises(expected_error):
            Connection(token, url)


@pytest.mark.parametrize(
    "route, expected_url",
    [
        ["", "https://api.github.com"],
        ["/", "https://api.github.com/"],
        ["repos", "https://api.github.com/repos"],
        ["/repos", "https://api.github.com/repos"],
    ],
)
def test_connection_resolve(route, expected_url):
    conn = Connection()
    assert conn.resolve(route) == expected_url


@pytest.mark.parametrize(
    "token, is_error, expected_header",
    [
        [None, True, {}],
        ["", True, {}],
        ["DUMMY_TOKEN", False, {"Authorization": "Bearer DUMMY_TOKEN"}],
        ["TOKEN_BIS", False, {"Authorization": "Bearer TOKEN_BIS"}],
    ],
)
def test_connection_authorization(token, is_error, expected_header):
    conn = Connection(token)
    if is_error:
        with pytest.raises(ValueError):
            conn.authorization
    else:
        assert conn.authorization == expected_header
