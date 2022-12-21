# Copyright (C) 2022, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Any, Dict, List

import requests

from .exceptions import HTTPRequestException

__all__ = ["Repository"]


class Repository:
    r"""Implements a Repository object

    >>> from ghapi.repos import Repository
    >>> repo = Repository("frgfm", "torch-cam")
    >>> repo.list_pulls()

    Args:
        owner: GitHub login of the repository's owner
        name: name of the repository
    """

    ROUTES: Dict[str, str] = {
        "pulls": "/repos/{owner}/{repo}/pulls",
    }

    def __init__(self, owner: str, name: str, conn: Union[Connection, None] = None) -> None:
        self.owner = owner
        self.name = name
        self.conn = conn if isinstance(conn, Connection) else Connection()
        self.reset()

    def reset(self) -> None:
        self._pulls: Union[List[Dict[str, Any]], None] = None

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(owner='{self.owner}', name='{self.name}')"

    @property
    def pulls(self, **kwargs: Any) -> List[Dict[str, Any]]:
        if not isinstance(self._pulls, list):
            response = requests.get(
                self.conn.resolve(self.ROUTES["pulls"].format(owner=self.owner, repo=self.name)),
                params=kwargs,
            )
            if response.status_code != 200:
                raise HTTPRequestException(response.status_code, response.text)
            self._pulls = response.json()
        return self._pulls

    def list_pulls(self, **kwargs: Any) -> List[int]:
        return [repo["number"] for repo in self.pulls]
