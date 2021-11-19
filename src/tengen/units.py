import re

import pint

ureg = pint.UnitRegistry()


def format_missing_carats_units(s: str):
    """Add missing carats to a malformed unit string.

    Will format a string 'm-1' to 'm^-1'.

    Parameters
    ----------
    s: str
        Unit string.

    Returns
    -------
    str
        Formatted unit string.
    """
    where = [m.start() for m in re.finditer("[-+][0-9]", s)]

    for count, i in enumerate(where):
        s = s[: i + count] + "^" + s[i + count :]

    where2 = [m.start() for m in re.finditer("[a-z ][0-9]", s)]

    for count, i in enumerate(where2):
        s = s[: i + count + 1] + "^" + s[i + count + 1 :]
    return s
