"""Test the ref_resolver module."""

from __future__ import absolute_import
import shutil
import tempfile

import pytest  # type: ignore

@pytest.fixture
def tmp_dir_fixture(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d

def test_Loader_initialisation_for_HOME_env_var(tmp_dir_fixture):
    import os
    from schema_salad.ref_resolver import Loader
    from requests import Session

    # Ensure HOME is set.
    os.environ["HOME"] = tmp_dir_fixture

    loader = Loader(ctx={})
    assert isinstance(loader.session, Session)

def test_Loader_initialisation_for_TMP_env_var(tmp_dir_fixture):
    import os
    from schema_salad.ref_resolver import Loader
    from requests import Session

    # Ensure HOME is missing.
    if "HOME" in os.environ:
        del os.environ["HOME"]
    # Ensure TMP is present.
    os.environ["TMP"] = tmp_dir_fixture

    loader = Loader(ctx={})
    assert isinstance(loader.session, Session)

def test_Loader_initialisation_with_neither_TMP_HOME_set(tmp_dir_fixture):
    import os
    from schema_salad.ref_resolver import Loader
    from requests import Session

    # Ensure HOME is missing.
    if "HOME" in os.environ:
        del os.environ["HOME"]
    if "TMP" in os.environ:
        del os.environ["TMP"]

    loader = Loader(ctx={})
    assert isinstance(loader.session, Session)

def test_DefaultFetcher_urljoin_win32(tmp_dir_fixture):
    import os
    import sys
    from schema_salad.ref_resolver import DefaultFetcher
    from requests import Session

    # Ensure HOME is set.
    os.environ["HOME"] = tmp_dir_fixture

    actual_platform = sys.platform
    try:
        # For this test always pretend we're on Windows
        sys.platform = "win32"
        fetcher = DefaultFetcher({}, None)
        # Relative path, same folder
        url = fetcher.urljoin("file:///C:/Users/fred/foo.cwl", "soup.cwl")
        assert url == "file:///C:/Users/fred/soup.cwl"
        # Relative path, sub folder
        url = fetcher.urljoin("file:///C:/Users/fred/foo.cwl", "foo/soup.cwl")
        assert url == "file:///C:/Users/fred/foo/soup.cwl"
        # relative climb-up path
        url = fetcher.urljoin("file:///C:/Users/fred/foo.cwl", "../alice/soup.cwl")
        assert url == "file:///C:/Users/alice/soup.cwl"

        # Path with drive: should not be treated as relative to directory
        # Note: \ would already have been converted to / by resolve_ref()
        url = fetcher.urljoin("file:///C:/Users/fred/foo.cwl", "c:/bar/soup.cwl")
        assert url == "file:///c:/bar/soup.cwl"
        # /C:/  (regular URI absolute path)
        url = fetcher.urljoin("file:///C:/Users/fred/foo.cwl", "/c:/bar/soup.cwl")
        assert url == "file:///c:/bar/soup.cwl"
        # Relative, change drive
        url = fetcher.urljoin("file:///C:/Users/fred/foo.cwl", "D:/baz/soup.cwl")
        assert url == "file:///d:/baz/soup.cwl"
        # Relative from root of base's D: drive
        url = fetcher.urljoin("file:///d:/baz/soup.cwl", "/foo/soup.cwl")
        assert url == "file:///d:/foo/soup.cwl"

        # resolving absolute non-drive URIs still works
        url = fetcher.urljoin("file:///C:/Users/fred/foo.cwl", "http://example.com/bar/soup.cwl")
        assert url == "http://example.com/bar/soup.cwl"
        # and of course relative paths from http://
        url = fetcher.urljoin("http://example.com/fred/foo.cwl", "soup.cwl")
        assert url == "http://example.com/fred/soup.cwl"

        # Stay on http:// and same host
        url = fetcher.urljoin("http://example.com/fred/foo.cwl", "/bar/soup.cwl")
        assert url == "http://example.com/bar/soup.cwl"


        # Security concern - can't resolve file: from http:
        with pytest.raises(ValueError):
            url = fetcher.urljoin("http://example.com/fred/foo.cwl", "file:///c:/bar/soup.cwl")
        # Drive-relative -- should NOT return "absolute" URI c:/bar/soup.cwl"
        # as that is a potential remote exploit
        with pytest.raises(ValueError):
            url = fetcher.urljoin("http://example.com/fred/foo.cwl", "c:/bar/soup.cwl")

    finally:
        sys.platform = actual_platform

def test_DefaultFetcher_urljoin_linux(tmp_dir_fixture):
    import os
    import sys
    from schema_salad.ref_resolver import DefaultFetcher
    from requests import Session

    # Ensure HOME is set.
    os.environ["HOME"] = tmp_dir_fixture

    actual_platform = sys.platform
    try:
        # Pretend it's Linux (e.g. not win32)
        sys.platform = "linux2"
        fetcher = DefaultFetcher({}, None)
        url = fetcher.urljoin("file:///home/fred/foo.cwl", "soup.cwl")
        assert url == "file:///home/fred/soup.cwl"

        url = fetcher.urljoin("file:///home/fred/foo.cwl", "../alice/soup.cwl")
        assert url == "file:///home/alice/soup.cwl"
        # relative from root
        url = fetcher.urljoin("file:///home/fred/foo.cwl", "/baz/soup.cwl")
        assert url == "file:///baz/soup.cwl"

        url = fetcher.urljoin("file:///home/fred/foo.cwl", "http://example.com/bar/soup.cwl")
        assert url == "http://example.com/bar/soup.cwl"

        url = fetcher.urljoin("http://example.com/fred/foo.cwl", "soup.cwl")
        assert url == "http://example.com/fred/soup.cwl"

        # Root-relative -- here relative to http host, not file:///
        url = fetcher.urljoin("http://example.com/fred/foo.cwl", "/bar/soup.cwl")
        assert url == "http://example.com/bar/soup.cwl"

        # Security concern - can't resolve file: from http:
        with pytest.raises(ValueError):
            url = fetcher.urljoin("http://example.com/fred/foo.cwl", "file:///bar/soup.cwl")

        # But this one is not "dangerous" on Linux
        fetcher.urljoin("http://example.com/fred/foo.cwl", "c:/bar/soup.cwl")

    finally:
        sys.platform = actual_platform
