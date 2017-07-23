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
