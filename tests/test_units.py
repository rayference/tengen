"""Test cases for the units module."""
from tengen.units import format_missing_carats_units


def test_format_missing_carats_units() -> None:
    """Format units as expected."""
    assert format_missing_carats_units("m2") == "m^2"
    assert format_missing_carats_units("m-2") == "m^-2"
    assert format_missing_carats_units("m2") == "m^2"
    assert format_missing_carats_units("m-2 s-1") == "m^-2 s^-1"
    assert format_missing_carats_units("m2 s-1") == "m^2 s^-1"
    assert format_missing_carats_units("d-8 m2 s-1 kg+4") == "d^-8 m^2 s^-1 kg^+4"
