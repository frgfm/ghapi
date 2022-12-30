import pytest

from ghapi.connection import Connection
from ghapi.exceptions import HTTPRequestException
from ghapi.pulls import PullRequest
from ghapi.repos import Repository
from ghapi.reviews import Comment, Review


@pytest.mark.parametrize(
    "path, body, line, kwargs, expected_dict",
    [
        ["README.md", "Thanks!", 1, {}, {"path": "README.md", "body": "Thanks!", "line": 1}],
        [
            "README.md",
            "Thanks!",
            2,
            {"start_line": 1},
            {"path": "README.md", "body": "Thanks!", "line": 2, "start_line": 1},
        ],
    ],
)
def test_comment(path, body, line, kwargs, expected_dict):
    comment = Comment(path, body, line, **kwargs)
    payload = comment.to_dict()
    assert isinstance(payload, dict)
    assert payload == expected_dict


def test_review_get_info(mock_review):
    conn = Connection(url="https://www.github.com")
    review = Review(PullRequest(Repository("frgfm", "Holocron", conn), 260), 1212580495)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        review.get_info()
    # Fix url
    review.conn.url = "https://api.github.com"
    # Set response
    review._info = mock_review
    out = review.get_info()
    assert len(out) == 6
    assert out["submitted_at"] == "2022-12-10T15:45:06Z"


def test_review_list_comments(mock_comment):
    conn = Connection(url="https://www.github.com")
    review = Review(PullRequest(Repository("frgfm", "Holocron", conn), 260), 1212580495)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        review.list_comments()
    # Fix url
    review.conn.url = "https://api.github.com"
    # Set response
    review._comments = [mock_comment]
    out = review.list_comments()
    assert len(out) == 1 and isinstance(out[0], dict) and len(out[0]) == 6


def test_review_from_comments(mock_review):
    conn = Connection(token="DUMMY_TOKEN", url="https://www.github.com")  # nosec B106
    pr = PullRequest(Repository("frgfm", "Holocron", conn), 260)
    comment = Comment("README.md", "Thanks!", 1)
    # Wrong api url
    with pytest.raises(HTTPRequestException):
        Review.from_comments(pr, "Thanks!", [comment])
