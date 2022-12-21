# Copyright (C) 2022, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from enum import Enum
from typing import Any, Dict, List

import requests

from .exceptions import HTTPRequestException
from .pulls import PullRequest

__all__ = ["Review"]

ROUTES: Dict[str, str] = {
    "create": "https://api.github.com/repos/{repo_name}/pulls/{pull_number}/reviews",
}


class ReviewAction(str, Enum):
    APPROVE = "APPROVE"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    COMMENT = "COMMENT"


class Review:
    r"""Implements a Review object

    >>> from ghapi_client.pulls import PullRequest
    >>> pr = PullRequest("frgfm/torch-cam", 187)
    >>> from ghapi_client.reviews import Review
    >>> review = Review(pr, token="MY_SECRET_TOKEN")
    >>> review.add_comment("README.md", "This is weird!", 9)
    >>> review.submit("Thanks for the PR!\nI left a few comments!")

    Args:
        pr: a pull request object
        token: your GitHub token (cf. https://github.com/settings/tokens)
    """

    def __init__(self, pr: PullRequest, token: str) -> None:
        self.pr = pr
        self.token = token
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
            ROUTES["create"].format(repo_name=self.pr.repo_name, pull_number=self.pr.pull_number),
            json={
                "body": body,
                "event": action,
                "comments": self.pending_comments,
            },
            headers=self._headers,
        )
        if response.status_code != 200:
            raise HTTPRequestException(response.status_code, response.text)
        self.response = response.json()

    @property
    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}
