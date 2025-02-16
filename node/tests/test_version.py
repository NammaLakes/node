import packaging.version
import pytest

import node


@pytest.mark.parametrize(
    "version,expected_version",
    ((node.__version__, "0.1.0"),),
)
def test_version_matches_expected(version: str, expected_version: str) -> None:
    assert version == expected_version


def test_version_is_valid() -> None:
    packaging.version.parse(node.__version__)
