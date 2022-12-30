# Copyright (C) 2022, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Any, Dict, List, Union

import requests

from .connection import Connection
from .exceptions import verify_status
from .utils import parse_user

__all__ = ["User"]


class User:
    r"""Implements a User object

    >>> from ghapi import User
    >>> user = User("frgfm")
    >>> user.get_info()

    Args:
        username: GitHub login
        conn: connection object
    """

    ROUTES: Dict[str, str] = {
        "info": "/users/{username}",
        "repos": "/users/{username}/repos",
    }

    def __init__(self, username: str, conn: Union[Connection, None] = None) -> None:
        if not isinstance(username, str) or len(username) == 0:
            raise ValueError("args `username` needs to be string of positive length.")
        self.username = username
        self.conn = conn if isinstance(conn, Connection) else Connection()
        self.reset()

    def reset(self) -> None:
        self._info: Union[Dict[str, Any], None] = None
        self._repos: Union[List[Dict[str, Any]], None] = None

    @property
    def info(self) -> Dict[str, Any]:
        if not isinstance(self._info, dict):
            self._info = verify_status(
                requests.get(self.conn.resolve(self.ROUTES["info"].format(username=self.username))),
                200,
            ).json()
        return self._info

    def get_info(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """Parses high-level information from the User"""

        return parse_user(self.info)

    def _list_repos(self, **kwargs: Any) -> List[Dict[str, Any]]:
        if not isinstance(self._repos, list):
            self._repos = verify_status(
                requests.get(
                    self.conn.resolve(self.ROUTES["repos"].format(username=self.username)),
                    params=kwargs,
                ),
                200,
            ).json()
        return self._repos

    def list_repos(self, **kwargs: Any) -> List[str]:
        """List the pull requests of a repository.

        Args:
            kwargs: query parameters of
                `GitHub API <https://docs.github.com/en/rest/repos/repos#list-repositories-for-a-user>`_
        Returns:
            list of repositories' names
        """
        return [pull["full_name"] for pull in self._list_repos(**kwargs)]
