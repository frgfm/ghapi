# Copyright (C) 2022, François-Guillaume Fernandez.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from enum import Enum
from typing import Any, Dict, List, Type, TypeVar, Union

import requests

from .connection import Connection
from .exceptions import verify_status
from .pulls import PullRequest
from .utils import parse_comment, parse_review

__all__ = ["Comment", "Review"]


T = TypeVar("T", bound="Review")


class ReviewAction(str, Enum):
    APPROVE = "APPROVE"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    COMMENT = "COMMENT"


class Comment:
    """Implements a comment object

    Args:
        path: the relative path to the file that necessitates a comment.
        body: the text of the review comment.
        line: the line of the blob in the pull request diff that the comment applies to. For a multi-line comment,
            the last line of the range that your comment applies to.
        kwargs: keyword arguments for comment (cf. `Review creation
            <https://docs.github.com/en/rest/pulls/reviews#create-a-review-for-a-pull-request--parameters>`_)
    """

    def __init__(self, path: str, body: str, line: int, **kwargs: Any) -> None:
        self.path = path
        self.body = body
        self.line = line
        self.kwargs = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Dumps the comment into a dictionary processable by GitHub API"""
        return dict(path=self.path, body=self.body, line=self.line, **self.kwargs)


class Review:
    r"""Implements a Review object

    >>> from ghapi import Repository, PullRequest, Review
    >>> pr = PullRequest(Repository("frgfm", "Holocron"), 260)
    >>> review = Review(pr, 1212580495)
    >>> review.get_info()

    Args:
        pr: a pull request object
        review_id: the review identifier
        conn: connection object
    """

    ROUTES: Dict[str, str] = {
        "create": "/repos/{owner}/{repo}/pulls/{pull_number}/reviews",
        "info": "/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}",
        "comments": "/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/comments",
    }

    def __init__(self, pr: PullRequest, review_id: int, conn: Union[Connection, None] = None) -> None:
        self.pr = pr
        self.review_id = review_id
        self.conn = conn if isinstance(conn, Connection) else pr.conn
        self.reset()

    def reset(self) -> None:
        self._info: Union[Dict[str, Any], None] = None
        self._comments: Union[List[Dict[str, Any]], None] = None

    @property
    def info(self) -> Dict[str, Any]:
        if not isinstance(self._info, dict):
            self._info = verify_status(
                requests.get(
                    self.conn.resolve(
                        self.ROUTES["info"].format(
                            owner=self.pr.repo.owner,
                            repo=self.pr.repo.name,
                            pull_number=self.pr.pull_number,
                            review_id=self.review_id,
                        )
                    )
                ),
                200,
            ).json()
        return self._info

    def get_info(self) -> Dict[str, Any]:
        """Parses high-level information from the review payload"""
        return parse_review(self.info)

    def _list_comments(self, **kwargs: Any) -> List[Dict[str, Any]]:
        if not isinstance(self._comments, list):
            self._comments = verify_status(
                requests.get(
                    self.conn.resolve(
                        self.ROUTES["comments"].format(
                            owner=self.pr.repo.owner,
                            repo=self.pr.repo.name,
                            pull_number=self.pr.pull_number,
                            review_id=self.review_id,
                        )
                    ),
                    params=kwargs,
                ),
                200,
            ).json()
        return self._comments

    def list_comments(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """List the comments of a Pull Request Review.

        Args:
            kwargs: query parameters of `List review comments
                <https://docs.github.com/en/rest/pulls/reviews#list-comments-for-a-pull-request-review>`_
        Returns:
            list of comments
        """
        return [parse_comment(comment) for comment in self._list_comments(**kwargs)]

    @classmethod
    def from_comments(
        cls: Type[T],
        pr: PullRequest,
        body: str,
        comments: List[Comment],
        action: ReviewAction = ReviewAction.COMMENT,
        conn: Union[Connection, None] = None,
    ) -> T:
        """Submit a review from comments

        >>> from ghapi import Repository, PullRequest, Review, Comment
        >>> pr = PullRequest(Repository("owner-login", "awesome-repo"), 1)
        >>> pr.conn.set_token("MY_DUMMY_TOKEN")
        >>> comment = Comment("README.md", "This is weird!", 9)
        >>> review = Review.from_comments(pr, "Thanks for the PR :pray:", [comment])

        Args:
            pr: a pull request object
            body: the body text of the pull request review.
            comments: the review comments
            action: the review action you want to perform.
            conn: connection object
        """

        # Create the object
        review = cls(pr, 1, conn)
        # Check that the connection is valid (accessing the token property will check that itself)
        isinstance(review.conn.token, str)

        # Submit the PR
        response = verify_status(
            requests.post(
                review.conn.resolve(
                    cls.ROUTES["create"].format(
                        owner=pr.repo.owner,
                        repo=pr.repo.name,
                        pull_number=pr.pull_number,
                    )
                ),
                json={
                    "body": body,
                    "event": action,
                    "comments": [comment.to_dict() for comment in comments],
                },
                headers=review.conn.authorization,
            ),
            200,
        ).json()
        # Updated the review id
        review.review_id = response["id"]
        # Fill the cache
        review._info = response

        return review
