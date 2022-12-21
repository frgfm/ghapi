import pytest

from ghapi.exceptions import HTTPRequestException
from ghapi.pulls import PullRequest
from ghapi.repos import Repository
from ghapi.reviews import Review


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
