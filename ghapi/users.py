# Copyright (C) 2022, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Any, Dict, List, Union

import requests

from .connection import Connection
from .exceptions import HTTPRequestException

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
            response = requests.get(self.conn.resolve(self.ROUTES["info"].format(username=self.username)))
            if response.status_code != 200:
                raise HTTPRequestException(response.status_code, response.text)

            self._info = response.json()
        return self._info

    def get_info(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """Parses high-level information from the User"""

        return {
            "login": self.info["login"],
            "name": self.info["name"],
            "company": self.info["company"],
            "blog": self.info["blog"],
            "location": self.info["location"],
            "bio": self.info["bio"],
            "email": self.info["email"],
            "twitter_username": self.info["twitter_username"],
            "num_followers": self.info["followers"],
            "num_public_repos": self.info["public_repos"],
            "created_at": self.info["created_at"],
            "updated_at": self.info["updated_at"],
        }

    def _list_repos(self, **kwargs: Any) -> List[Dict[str, Any]]:
        if not isinstance(self._repos, list):
            response = requests.get(
                self.conn.resolve(self.ROUTES["repos"].format(username=self.username)),
                params=kwargs,
            )
            if response.status_code != 200:
                raise HTTPRequestException(response.status_code, response.text)
            self._repos = response.json()
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
