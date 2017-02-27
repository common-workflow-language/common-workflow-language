"""Test the ref_resolver module."""

def test_Loader_initialisation_when_HOME_env_is_missing():
    from schema_salad.ref_resolver import Loader
    import os

    # Simulate missing HOME environment variable.
    if "HOME" in os.environ:
        del os.environ["HOME"]
    Loader(ctx={})
