# Copyright (C) 2022, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import re
from typing import Any, Dict, List, Tuple, Union

import requests

from .connection import Connection
from .exceptions import verify_status
from .repos import Repository
from .utils import parse_comment, parse_pull, parse_review

__all__ = ["PullRequest"]


OInt = Union[int, None]
FILE_PATTERN = re.compile(r"^diff\s\-\-git\sa/(?P<prev>\S+)\sb/(?P<new>\S+)$")
SECTION_PATTERN = re.compile(r"^@@\s\-(?P<prev>\d+),\d+\s\+(?P<new>\d+)(,\d+)*\s@@")


def parse_file_diff(line_split: List[str]) -> List[Tuple[OInt, OInt, OInt, OInt, int, int]]:
    # Spot the section headers
    section_idcs = [idx for idx, line in enumerate(line_split) if line.startswith("@@ -")]
    section_limits = [(_prev, _next) for _prev, _next in zip(section_idcs, section_idcs[1:] + [len(line_split)])]
    section_info = [
        SECTION_PATTERN.match(line_split[idx]).groupdict() for idx in section_idcs  # type: ignore[union-attr]
    ]
    # Split each section into blocks
    blocks = []
    for line_info, (_start, _end) in zip(section_info, section_limits):
        left_idx, right_idx = int(line_info["prev"]), int(line_info["new"])
        abs_start, left_start, right_start = None, None, None
        for idx, line in enumerate(line_split[_start + 1 : _end]):
            # Counter update
            if not line.startswith("-"):
                right_idx += 1
            if not line.startswith("+"):
                left_idx += 1

            # Block
            if line.startswith("-") or line.startswith("+"):
                if not isinstance(abs_start, int):
                    abs_start = _start + 1 + idx
                # Left block
                if line.startswith("-") and not isinstance(left_start, int):
                    left_start = left_idx - 1
                # Right block
                elif line.startswith("+") and not isinstance(right_start, int):
                    right_start = right_idx - 1
            # End of block
            elif isinstance(abs_start, int):
                abs_end = _start + idx
                left_end = left_idx - 2 if isinstance(left_start, int) else None
                right_end = right_idx - 2 if isinstance(right_start, int) else None
                blocks.append((left_start, left_end, right_start, right_end, abs_start, abs_end))
                abs_start, left_start, right_start = None, None, None

        # Final one
        if isinstance(abs_start, int):
            abs_end = _start + 1 + idx
            left_end = left_idx - 1 if isinstance(left_start, int) else None
            right_end = right_idx - 1 if isinstance(right_start, int) else None
            blocks.append((left_start, left_end, right_start, right_end, abs_start, abs_end))

    return blocks


def parse_diff_body(diff_body: str) -> Dict[str, List[Dict[str, Any]]]:
    """This will need to be refactored using regex"""
    # Split by files
    line_split = diff_body.split("\n")
    file_limits = [idx for idx, line in enumerate(line_split) if line.startswith("diff --git ")]
    file_names = [
        FILE_PATTERN.match(line_split[idx]).groupdict()["new"] for idx in file_limits  # type: ignore[union-attr]
    ]
    parsed_files = [
        parse_file_diff(line_split[_start:_end])
        for _start, _end in zip(file_limits, file_limits[1:] + [len(line_split)])
    ]

    return {
        file_name: [
            {
                "start": {"left": left_start, "right": right_start},
                "end": {"left": left_end, "right": right_end},
                "text": "\n".join(line_split[file_start + abs_start : file_start + abs_end + 1]),
            }
            for left_start, left_end, right_start, right_end, abs_start, abs_end in parsed_file
        ]
        for file_name, parsed_file, file_start in zip(file_names, parsed_files, file_limits)
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

    ROUTES = {
        "info": "/repos/{owner}/{repo}/pulls/{pull_number}",
        "comments": "/repos/{owner}/{repo}/issues/{pull_number}/comments",
        "review-comments": "/repos/{owner}/{repo}/pulls/{pull_number}/comments",
        "reviews": "/repos/{owner}/{repo}/pulls/{pull_number}/reviews",
    }

    def __init__(self, repo: Repository, pull_number: int, conn: Union[Connection, None] = None) -> None:
        self.repo = repo
        self.pull_number = pull_number
        self.conn = conn if isinstance(conn, Connection) else repo.conn
        self.reset()

    def reset(self) -> None:
        self._info: Union[Dict[str, Any], None] = None
        self._diff: Union[str, None] = None
        self._comments: Union[List[Dict[str, Any]], None] = None
        self._review_comments: Union[List[Dict[str, Any]], None] = None
        self._reviews: Union[List[Dict[str, Any]], None] = None

    def _query(
        self, subroute: str, params: Union[Dict[str, str], None] = None, headers: Union[Dict[str, str], None] = None
    ) -> requests.models.Response:
        return verify_status(
            requests.get(
                self.conn.resolve(subroute),
                params={} if params is None else params,
                headers={} if headers is None else headers,
            ),
            200,
        )

    @property
    def info(self) -> Dict[str, Any]:
        if not isinstance(self._info, dict):
            self._info = self._query(
                self.ROUTES["info"].format(owner=self.repo.owner, repo=self.repo.name, pull_number=self.pull_number)
            ).json()
        return self._info

    def get_info(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """Parses high-level information from the Pull Request"""
        return parse_pull(self.info)

    @property
    def diff(self) -> str:
        if not isinstance(self._diff, str):
            self._diff = self._query(
                self.ROUTES["info"].format(owner=self.repo.owner, repo=self.repo.name, pull_number=self.pull_number),
                headers={"Accept": "application/vnd.github.v4.diff"},
            ).content.decode()
        return self._diff

    def get_diff(self) -> Dict[str, List[Dict[str, Any]]]:
        """Parses the PR diff

        Returns:
            a dictionary where each key is a file path and each value is a list of dict. Each dict has three keys:
                the start line, the end line, and the actuall diff string.
        """
        return parse_diff_body(self.diff)

    def _list_comments(self, **kwargs: Any) -> List[Dict[str, Any]]:
        if not isinstance(self._comments, list):
            self._comments = self._query(
                self.ROUTES["comments"].format(
                    owner=self.repo.owner, repo=self.repo.name, pull_number=self.pull_number
                ),
                params=kwargs,
            ).json()
        return self._comments

    def list_comments(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """List the comments of a Pull Request.

        Args:
            kwargs: query parameters of `List issue comments
                <https://docs.github.com/en/rest/issues/comments#list-issue-comments>`_
        Returns:
            list of comments
        """
        return [parse_comment(comment) for comment in self._list_comments(**kwargs)]

    def _list_review_comments(self, **kwargs: Any) -> List[Dict[str, Any]]:
        if not isinstance(self._review_comments, list):
            self._review_comments = self._query(
                self.ROUTES["review-comments"].format(
                    owner=self.repo.owner, repo=self.repo.name, pull_number=self.pull_number
                ),
                params=kwargs,
            ).json()
        return self._review_comments

    def list_review_comments(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """List the review comments of a Pull Request.

        Args:
            kwargs: query parameters of `List review comments
                <https://docs.github.com/en/rest/pulls/comments#list-review-comments-on-a-pull-request>`_
        Returns:
            list of review comments
        """
        return [parse_comment(comment) for comment in self._list_review_comments(**kwargs)]

    def _list_reviews(self, **kwargs: Any) -> List[Dict[str, Any]]:
        if not isinstance(self._reviews, list):
            self._reviews = self._query(
                self.ROUTES["reviews"].format(owner=self.repo.owner, repo=self.repo.name, pull_number=self.pull_number),
                params=kwargs,
            ).json()
        return self._reviews

    def list_reviews(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """List the reviews of a Pull Request.

        Args:
            kwargs: query parameters of `List reviews
                <https://docs.github.com/en/rest/pulls/reviews#list-reviews-for-a-pull-request>`_
        Returns:
            list of reviews
        """
        return [parse_review(review) for review in self._list_reviews(**kwargs)]
