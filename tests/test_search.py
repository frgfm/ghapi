import pytest

from ghapi.connection import Connection
from ghapi.exceptions import HTTPRequestException
from ghapi.search import Search


@pytest.mark.parametrize(
    "token, expected_error",
    [
        [None, None],
        ["DUMMY_TOKEN", None],
    ],
)
def test_search_constructor(token, expected_error):
    conn = Connection(token)

    if expected_error is None:
        search = Search(conn)
        assert isinstance(search.conn, Connection)
        if isinstance(token, str):
            assert search.conn.token == token
    else:
        with pytest.raises(ValueError):
            Search(conn)


@pytest.mark.parametrize(
    "query, kwargs, token, expected_error, total_count",
    [
        ["repo: ", {}, None, HTTPRequestException, None],
        ["repo:frgfm/torch-cam", {}, None, None, 1],
    ],
)
def test_search_query_repos(query, kwargs, token, expected_error, total_count):
    conn = Connection(token)
    search = Search(conn)

    if expected_error is None:
        result = search.query_repos(query, **kwargs)
        assert result["total_count"] == total_count
    else:
        with pytest.raises(expected_error):
            search.query_repos(query, **kwargs)


@pytest.mark.parametrize(
    "query, kwargs, token, expected_error, total_count",
    [
        ["user: ", {}, None, HTTPRequestException, None],
        ["user:frgfm", {}, None, None, 1],
    ],
)
def test_search_query_users(query, kwargs, token, expected_error, total_count):
    conn = Connection(token)
    search = Search(conn)

    if expected_error is None:
        result = search.query_users(query, **kwargs)
        assert result["total_count"] == total_count
    else:
        with pytest.raises(expected_error):
            search.query_users(query, **kwargs)
