# Copyright (C) 2022, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Union

import requests

__all__ = ["HTTPRequestException"]


class HTTPRequestException(Exception):
    def __init__(self, status_code: int, response_message: Union[str, None] = None) -> None:
        self.status_code = status_code
        self.response_message = response_message

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, response_message={self.response_message!r})"


def verify_status(response: requests.models.Response, status_code: int) -> requests.models.Response:
    if response.status_code != status_code:
        raise HTTPRequestException(response.status_code, response.text)
    return response
