"""Test mmdio."""

import mmdio


def test_import() -> None:
    """Test that the app can be imported."""
    assert isinstance(mmdio.__name__, str)
