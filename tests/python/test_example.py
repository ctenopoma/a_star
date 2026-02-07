import pytest

from a_star import validate_name



def test_validate_name_success() -> None:
    assert validate_name("Alice") == "Alice"


def test_validate_name_rejects_blank() -> None:
    with pytest.raises(ValueError):
        validate_name("   ")
