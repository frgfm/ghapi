# Copyright (C) 2022, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Any, Dict, List, Tuple, Union

import requests

from .connection import Connection
from .exceptions import HTTPRequestException
from .repos import Repository

__all__ = ["PullRequest"]


def parse_diff_body(diff_body: str) -> Dict[str, List[Tuple[str, str]]]:
    """This will need to be refactored using regex"""
    # Split by files
    file_split = diff_body.split("diff --git ")[1:]
    file_names = [file_str.split("\n")[0].split(" b/")[1].strip() for file_str in file_split]

    # Split by sections
    file_diffs = [
        [section.partition("\n") for section in file_str.rpartition(f"{file_name}\n")[-1].split("@@ -")[1:]]
        for file_str, file_name in zip(file_split, file_names)
    ]

    return {
        file_name: [(f"@@ -{section_diff[0]}", section_diff[-1]) for section_diff in file_diff]
        for file_name, file_diff in zip(file_names, file_diffs)
    }


class PullRequest:
    """Implements a Pull Request object

    >>> from ghapi import Repository, PullRequest
    >>> pr = PullRequest(Repository("frgfm", "torch-cam"), 187)
    >>> pr.get_info()

    Args:
        repo: the parent repository object
        pull_number: the PR number
        conn: connection object
    """

    ROUTE = "/repos/{owner}/{repo}/pulls/{pull_number}"

    def __init__(self, repo: Repository, pull_number: int, conn: Union[Connection, None] = None) -> None:
        self.repo = repo
        self.pull_number = pull_number
        self.conn = conn if isinstance(conn, Connection) else repo.conn
        self.reset()

    def reset(self) -> None:
        self._info: Union[Dict[str, Any], None] = None
        self._diff: Union[str, None] = None

    @property
    def info(self) -> Dict[str, Any]:
        if not isinstance(self._info, dict):
            response = requests.get(
                self.conn.resolve(
                    self.ROUTE.format(owner=self.repo.owner, repo=self.repo.name, pull_number=self.pull_number)
                )
            )
            if response.status_code != 200:
                raise HTTPRequestException(response.status_code, response.text)

            self._info = response.json()
        return self._info

    def get_info(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """Parses high-level information from the Pull Request"""

        return {
            "title": self.info["title"],
            "created_at": self.info["created_at"],
            "description": self.info["body"],
            "labels": self.info["labels"],
            "user": self.info["user"]["login"],
            "mergeable": self.info["mergeable"],
            "changed_files": self.info["changed_files"],
            "additions": self.info["additions"],
            "deletions": self.info["deletions"],
            "base": {"branch": self.info["base"]["ref"], "sha": self.info["base"]["sha"]},
            "head": {
                "repo": self.info["head"]["repo"]["full_name"],
                "branch": self.info["head"]["ref"],
                "sha": self.info["head"]["sha"],
            },
        }

    @property
    def diff(self) -> str:
        if not isinstance(self._diff, str):
            response = requests.get(
                self.conn.resolve(
                    self.ROUTE.format(owner=self.repo.owner, repo=self.repo.name, pull_number=self.pull_number)
                ),
                headers={"Accept": "application/vnd.github.v4.diff"},
            )
            if response.status_code != 200:
                raise HTTPRequestException(response.status_code, response.text)

            self._diff = response.content.decode()
        return self._diff

    def get_diff(self) -> Dict[str, List[Tuple[str, str]]]:
        """Parses the PR diff

        Returns:
            a dictionary where each key is a file path and each value is a list of tuples. Each tuple has two elements:
                the diff header, and the actuall diff string.
        """
        return parse_diff_body(self.diff)
