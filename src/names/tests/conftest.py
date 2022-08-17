import pytest

from names.name import Names


@pytest.fixture
def name_class():
    return Names()
