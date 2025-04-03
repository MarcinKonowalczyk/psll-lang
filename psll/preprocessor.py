import re


def read_file(filename: str) -> str:
    """Read a file and return the contents as a string"""
    with open(filename) as f:
        text = f.read()
    return text


_SUBS = (
    (r"//.*", ""),  # Remove comments
    (r"\n+", ""),  # Remove newlines
    (r"((?<=^)\s+|\s+(?=$))", ""),  # No trailing or leading whitespace
    (r"((?<=\()\s+|\s+(?=\)))", ""),  # Spaces inside brackets
    (r"(?<=\))(?=\()", " "),  # Put single spaces between crammed brackets
)

SUBS = tuple((re.compile(a), b) for a, b in _SUBS)


def preprocess(text: str) -> str:
    """Remove comments and make sure all the lines are in correct brackets"""

    for regex, replacement in SUBS:
        text = regex.sub(replacement, text)

    return text
