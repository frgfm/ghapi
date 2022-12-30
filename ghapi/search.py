# Copyright (C) 2022, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from enum import Enum
from typing import Any, Dict, Union

import requests

from .connection import Connection
from .exceptions import verify_status

__all__ = ["Search"]


class RepoSort(str, Enum):
    STARS = "stars"
    FORKS = "forks"
    HELP = "help-wanted-issues"
    UPDATED = "updated"


class UserSort(str, Enum):
    FOLLOWERS = "followers"
    REPOS = "repositories"
    JOINED = "joined"


class Order(str, Enum):
    ASC = "asc"
    DESC = "desc"


class Search:
    r"""Implements a Search object

    >>> from ghapi import Search
    >>> search = Search()
    >>> search.query_repos("repo:frgfm/torch-cam")

    Args:
        conn: connection object
    """

    ROUTES: Dict[str, str] = {
        "repos": "/search/repositories",
        "users": "/search/users",
    }

    def __init__(self, conn: Union[Connection, None] = None) -> None:
        self.conn = conn if isinstance(conn, Connection) else Connection()

    def _query(self, route_id: str, query: str, **kwargs: Any) -> Dict[str, Any]:
        _params = {"q": query, **kwargs}
        route_url = self.conn.resolve(self.ROUTES[route_id])
        return verify_status(requests.get(route_url, params=_params), 200).json()

    def query_repos(
        self,
        query: str,
        sort: Union[RepoSort, None] = None,
        order: Order = Order.DESC,
        per_page: int = 30,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Search for repositories.

        Args:
            query: search query
                (cf. https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories)
            sort: Sorts the results of your query by number of stars, forks, or help-wanted-issues or how recently
                the items were updated. Default: best match
            order: Determines whether the first search result returned is the highest number of matches (desc) or
                lowest number of matches (asc). This parameter is ignored unless you provide sort.
            per_page: The number of results per page (max 100).
            page: Page number of the results to fetch.
        Returns:
            a dictionary with 3 keys: total_count (number of results), incomplete_results (whether all the results were
                sent in the response), items (the displayed results)
        """
        return self._query("repos", query, sort=sort, order=order, per_page=per_page, page=page)

    def query_users(
        self,
        query: str,
        sort: Union[UserSort, None] = None,
        order: Order = Order.DESC,
        per_page: int = 30,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Search for users.

        Args:
            query: search query
                (cf. https://docs.github.com/en/search-github/searching-on-github/searching-users)
            sort: Sorts the results of your query by number of followers or repositories, or when the person
                joined GitHub. Default: best match
            order: Determines whether the first search result returned is the highest number of matches (desc) or
                lowest number of matches (asc). This parameter is ignored unless you provide sort.
            per_page: The number of results per page (max 100).
            page: Page number of the results to fetch.
        Returns:
            a dictionary with 3 keys: total_count (number of results), incomplete_results (whether all the results were
                sent in the response), items (the displayed results)
        """
        return self._query("users", query, sort=sort, order=order, per_page=per_page, page=page)
