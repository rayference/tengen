"""Test cases for the resources module."""
import pytest

from tengen.resources import (
    Resource,
    transform_thuillier_2003,
    Coddington2021Resolution,
    coddington_2021_url,
    transform_coddington_2021,
)


def test_resource() -> None:
    pass


def test_transform_thuillier_2003() -> None:
    pass


@pytest.mark.parametrize("resolution", [x for x in Coddington2021Resolution])
def test_coddington_2021_url(resolution) -> None:
    assert isinstance(coddington_2021_url(resolution), str)


def test_transform_coddington_2021() -> None:
    pass
