import pytest

from ghapi.exceptions import HTTPRequestException
from ghapi.repos import Repository


@pytest.mark.parametrize(
    "owner, name, expected_error, expected_repr",
    [
        [None, "ghapi", ValueError, None],
        ["", "ghapi", ValueError, None],
        ["frgfm", None, ValueError, None],
        ["frgfm", "", ValueError, None],
        ["frgfm", "ghapi", None, "Repository(owner='frgfm', name='ghapi')"],
    ],
)
def test_repository_repr(owner, name, expected_error, expected_repr):
    if expected_error is None:
        repo = Repository(owner, name)
        assert str(repo) == expected_repr
    else:
        with pytest.raises(expected_error):
            Repository(owner, name)


@pytest.mark.parametrize(
    "owner, name, expected_error",
    [
        ["frgfm", "fantasy-repo", HTTPRequestException],
        ["frgfm", "ghapi", None],
    ],
)
def test_repository_list_pulls(owner, name, expected_error):
    if expected_error is None:
        pulls = Repository(owner, name).list_pulls(state="all")
        assert isinstance(pulls, list) and len(pulls) > 1
        assert all(isinstance(elt, int) and elt >= 1 for elt in pulls)
    else:
        with pytest.raises(expected_error):
            Repository(owner, name).list_pulls()
