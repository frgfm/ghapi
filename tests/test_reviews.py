import pytest

from ghapi.connection import Connection
from ghapi.exceptions import HTTPRequestException
from ghapi.pulls import PullRequest
from ghapi.repos import Repository
from ghapi.reviews import Review


@pytest.mark.parametrize(
    "owner, repo, pull_number, token, expected_error",
    [
        ["owner", "repo", 2, None, ValueError],
        ["owner", "repo", 2, "DUMMY_TOKEN", None],
    ],
)
def test_review_constructor(owner, repo, pull_number, token, expected_error):
    conn = Connection(token)
    pr = PullRequest(Repository(owner, repo, conn), pull_number)

    if expected_error is None:
        review = Review(pr)
        assert isinstance(review.pr, PullRequest)
        assert isinstance(review.conn, Connection) and review.conn.token == token
        assert len(review.pending_comments) == 0
    else:
        with pytest.raises(ValueError):
            Review(pr)


@pytest.mark.parametrize(
    "owner, repo, pull_number, path, body, line, kwargs, expected_comment",
    [
        ["owner", "repo", 2, "README.md", "Weird", 1, {}, {"path": "README.md", "body": "Weird", "line": 1}],
        [
            "owner",
            "repo",
            2,
            "README.md",
            "Weird",
            3,
            {"start_line": 1},
            {"path": "README.md", "body": "Weird", "line": 3, "start_line": 1},
        ],
    ],
)
def test_review_stage_comment(owner, repo, pull_number, path, body, line, kwargs, expected_comment):
    pr = PullRequest(Repository(owner, repo), pull_number)
    pr.conn.set_token("DUMMY_TOKEN")
    review = Review(pr)
    assert len(review.pending_comments) == 0
    review.stage_comment(path, body, line, **kwargs)
    assert len(review.pending_comments) == 1
    assert review.pending_comments[0] == expected_comment


@pytest.mark.parametrize(
    "owner, repo, pull_number, path, body, line, kwargs, expected_comment",
    [
        ["owner", "repo", 2, "README.md", "Weird", 1, {}, {"path": "README.md", "body": "Weird", "line": 1}],
    ],
)
def test_review_submit(owner, repo, pull_number, path, body, line, kwargs, expected_comment):
    pr = PullRequest(Repository(owner, repo), pull_number)
    pr.conn.set_token("DUMMY_TOKEN")
    review = Review(pr)
    review.stage_comment(path, body, line, **kwargs)

    with pytest.raises(HTTPRequestException):
        review.submit("Thanks for the PR!")
