# Copyright (C) 2022, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from enum import Enum
from typing import Any, Dict, List, Union

import requests

from .connection import Connection
from .exceptions import HTTPRequestException
from .pulls import PullRequest

__all__ = ["Review"]


class ReviewAction(str, Enum):
    APPROVE = "APPROVE"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    COMMENT = "COMMENT"


class Review:
    r"""Implements a Review object

    >>> from ghapi import Repository, PullRequest, Review
    >>> pr = PullRequest(Repository("frgfm", "torch-cam"), 187)
    >>> pr.conn.set_token("MY_DUMMY_TOKEN")
    >>> review = Review(pr)
    >>> review.stage_comment("README.md", "This is weird!", 9)
    >>> review.submit("Thanks for the PR!\nI left a few comments!")

    Args:
        pr: a pull request object
        conn: connection object
    """

    ROUTES: Dict[str, str] = {
        "create": "/repos/{owner}/{repo}/pulls/{pull_number}/reviews",
    }

    def __init__(self, pr: PullRequest, conn: Union[Connection, None] = None) -> None:
        self.pr = pr
        self.conn = conn if isinstance(conn, Connection) else pr.conn
        # Check that the connection is valid (accessing the token property will check that itself)
        isinstance(self.conn.token, str)
        # Create the pending review
        self.pending_comments: List[Dict[str, Any]] = []

    def stage_comment(self, path: str, body: str, line: int, **kwargs: Any) -> None:
        """Stage a comment for the review

        Args:
            path: the relative path to the file that necessitates a comment.
            body: the text of the review comment.
            line: the line of the blob in the pull request diff that the comment applies to. For a multi-line comment,
                the last line of the range that your comment applies to.
            kwargs: keyword arguments for comment creation
        """
        self.pending_comments.append(dict(path=path, body=body, line=line, **kwargs))

    def submit(self, body: str, action: ReviewAction = ReviewAction.COMMENT) -> None:
        """Submit a review

        Args:
            body: the body text of the pull request review.
            action: the review action you want to perform.
        """
        response = requests.post(
            self.conn.resolve(
                self.ROUTES["create"].format(
                    owner=self.pr.repo.owner,
                    repo=self.pr.repo.name,
                    pull_number=self.pr.pull_number,
                )
            ),
            json={
                "body": body,
                "event": action,
                "comments": self.pending_comments,
            },
            headers=self.conn.authorization,
        )
        if response.status_code != 200:
            raise HTTPRequestException(response.status_code, response.text)
        self.response = response.json()
