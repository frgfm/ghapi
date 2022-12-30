# Copyright (C) 2022, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Any, Dict, List, Union

import requests

from .connection import Connection
from .exceptions import verify_status
from .utils import parse_repo

__all__ = ["Repository"]


class Repository:
    r"""Implements a Repository object

    >>> from ghapi.repos import Repository
    >>> repo = Repository("frgfm", "torch-cam")
    >>> repo.list_pulls()

    Args:
        owner: GitHub login of the repository's owner
        name: name of the repository
        conn: connection object
    """

    ROUTES: Dict[str, str] = {
        "info": "/repos/{owner}/{repo}",
        "pulls": "/repos/{owner}/{repo}/pulls",
    }

    def __init__(self, owner: str, name: str, conn: Union[Connection, None] = None) -> None:
        if (not isinstance(owner, str) or len(owner) == 0) or (not isinstance(name, str) or len(name) == 0):
            raise ValueError("args `owner` and `name` need to be strings of positive length.")
        self.owner = owner
        self.name = name
        self.conn = conn if isinstance(conn, Connection) else Connection()
        self.reset()

    def reset(self) -> None:
        self._info: Union[Dict[str, Any], None] = None
        self._pulls: Union[List[Dict[str, Any]], None] = None

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(owner='{self.owner}', name='{self.name}')"

    @property
    def info(self) -> Dict[str, Any]:
        if not isinstance(self._info, dict):
            self._info = verify_status(
                requests.get(self.conn.resolve(self.ROUTES["info"].format(owner=self.owner, repo=self.name))),
                200,
            ).json()
        return self._info

    def get_info(self) -> Dict[str, Any]:
        """Parses high-level information from the Repository"""
        return parse_repo(self.info)

    def _list_pulls(self, **kwargs: Any) -> List[Dict[str, Any]]:
        if not isinstance(self._pulls, list):
            self._pulls = verify_status(
                requests.get(
                    self.conn.resolve(self.ROUTES["pulls"].format(owner=self.owner, repo=self.name)),
                    params=kwargs,
                ),
                200,
            ).json()
        return self._pulls

    def list_pulls(self, **kwargs: Any) -> List[int]:
        """List the pull requests of a repository.

        Args:
            kwargs: query parameters of `GitHub API <https://docs.github.com/en/rest/pulls/pulls#list-pull-requests>`_
        Returns:
            list of pull request numbers
        """
        return [pull["number"] for pull in self._list_pulls(**kwargs)]
