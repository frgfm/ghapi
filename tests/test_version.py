import ghapi_client


def test_version():
    version_split = ghapi_client.__version__.split(".")
    assert len(version_split) in (3, 4)
    assert all(elt.isdigit() for elt in version_split[:3])
    if len(version_split) == 4:
        assert version_split[-1][0].isalpha()
