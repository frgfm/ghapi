# Copyright (C) 2022, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Dict, Union
from urllib.parse import urljoin

import requests

from .exceptions import verify_status

__all__ = ["Connection"]


class Connection:
    """Implements a GH API Connection object

    >>> from ghapi.connection import Connection
    >>> con = Connection("DUMMY_TOKEN")

    Args:
        token: your GitHub token (cf. https://github.com/settings/tokens)
        url: URL to the Github API
    """

    def __init__(self, token: Union[str, None] = None, url: str = "https://api.github.com") -> None:
        # Check the URL
        verify_status(requests.get(url), 200)

        self.url = url
        self.set_token(token)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(url='{self.url}')"

    def resolve(self, route: str) -> str:
        """Resolves the absolute URL of the route

        Args:
            route: relative URL of the route
        Returns:
            the absolute URL of the route
        """
        return urljoin(self.url, route)

    def set_token(self, token: Union[str, None]) -> None:
        """Sets the token used for this connection

        Args:
            token: your GitHub token (cf. https://github.com/settings/tokens)
        """
        self._token = token

    @property
    def token(self):
        if not isinstance(self._token, str) or len(self._token) == 0:
            raise ValueError("token not set. Please use the `set_token` method.")
        return self._token

    @property
    def authorization(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}
