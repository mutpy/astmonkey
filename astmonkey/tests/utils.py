import sys


def check_version(from_inclusive=None, to_exclusive=None):
    if (not from_inclusive or sys.version_info >= from_inclusive) \
            and (not to_exclusive or sys.version_info < to_exclusive):
        return True
    return False
