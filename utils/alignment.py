# -*- coding: utf-8 -*-

import re
import unicodedata
from sys import platform as _platform


def remove_ansi_escape(string):
    """Remove ANSI escape code.

    Parameters
    ----------
    string : string
        The string to be handled.

    Examples
    --------
    >>> remove_ansi_escape('\033[94mHello\033[0m')
    'Hello'

    >>> remove_ansi_escape('\033[4mHi\033[0m')
    'Hi'
    """
    # ansi_escape = re.compile(r'''
    #         \x1B  # ESC
    #         (?:   # 7-bit C1 Fe (except CSI)
    #             [@-Z\\-_]
    #         |     # or [ for CSI, followed by a control sequence
    #             \[
    #             [0-?]*  # Parameter bytes
    #             [ -/]*  # Intermediate bytes
    #             [@-~]   # Final byte
    #         )
    #     ''', re.VERBOSE)
    ansi_escape = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", string)


def is_wide(ch):
    """Check is the character wide or not.

    Parameters
    ----------
    ch : character
        The character to be checked.

    Examples
    --------
    >>> is_wide('鄭')
    True

    >>> is_wide('a')
    False
    """
    res = unicodedata.east_asian_width(ch)
    if res == "A":
        # Ambiguous
        if _platform.startswith("linux"):
            # Linux
            return False
        elif _platform.startswith("win") or _platform.startswith("cygwin"):
            # Windows
            return True
        elif _platform.startswith("darwin"):
            # Mac OS X
            return False
        else:
            # Other OS
            return False
    elif res == "F":
        # Fullwidth
        return True
    elif res == "H":
        # Halfwidth
        return False
    elif res == "N":
        # Neutral (Not East Asian)
        return False
    elif res == "Na":
        # Narrow
        return False
    elif res == "W":
        # Wide
        return True
    else:
        # No such case
        return False


def get_width(string):
    """Get width of string.

    Parameters
    ----------
    string : str
        Target string.

    Examples
    --------
    >>> get_width("你好")
    4

    >>> get_width("Hello")
    5

    >>> get_width("❤️")
    1

    >>> get_width("")
    0
    """

    if not string:
        return 0

    string = remove_ansi_escape(string)

    width = 0
    # combining_char = "[?([\u0300-\u036f]"
    variation_selector = "[?([\ufe00-\ufe0f]"

    for i in range(len(string)):
        # Combining character
        # if re.match(combining_char, string[i]):
        if unicodedata.combining(string[i]):
            if i == 0:
                # If at beginning of the line alone
                ch_width = 1
            else:
                ch_width = 0
        elif re.match(variation_selector, string[i]):
            if i == 0:
                # If at beginning of the line alone
                ch_width = 1
            else:
                ch_width = 0
        # Fullwidth character
        elif is_wide(string[i]):
            ch_width = 2
        # Neutral character
        else:
            ch_width = 1

        width += ch_width

    return width


def align(string, dir="l", length=12):
    """Align string in given length.

    Parameters
    ----------
    string : str
        Target string.
    dir : str
        'l' means left, 'r' means right.
    length : int
        Align length.

    Examples
    >>> align("Hello", dir='r', length=8)
    '   Hello'

    >>> align("你好", dir='r', length=8)
    '    你好'
    """

    if not string:
        return ""

    diff = length - get_width(string)

    if diff < 0:
        # print("Error: alighment length smaller than actual string length")
        # return None
        diff = 1

    if dir == "l":
        ret_str = string + " " * diff
    elif dir == "r":
        ret_str = " " * diff + string
    else:
        # No such direction
        return None

    return ret_str
