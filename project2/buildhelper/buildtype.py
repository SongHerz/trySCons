#!/usr/bin/env python

import re


def default(build_types):
    """
    Return default build type in str.

    build_types     [build type in str]
    """
    assert isinstance(build_types, list) and len(build_types) > 0
    assert all(map(lambda x: isinstance(x, str), build_types))
    return build_types[0]


def help_msg(build_types):
    """
    Return build type help message.
    build_types [str]   build type names
    default     str     default build type
    """
    return 'build types {{{}}}, default: {}'.format(', '.join(build_types), default(build_types))


def from_str(line):
    """
    Return ([build type in str], default build type in str), when build type can be extracted from string.
            None, when no build type can be extracted from string.
    line    str     A line.

    NOTE: Information extraction method follows msg format in build_type_help_msg(...).
    """
    ptn = re.compile(r'build types \{(.*)\}, default:\s*(\S+)')
    m = ptn.search(line)
    if not m:
        return None

    return (map(lambda x: x.strip(), m.group(1).split(',')), m.group(2))
