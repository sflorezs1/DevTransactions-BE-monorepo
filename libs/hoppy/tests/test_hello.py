"""Hello unit test module."""

from hoppy.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello hoppy"
