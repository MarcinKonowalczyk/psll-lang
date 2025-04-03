from . import PsllSyntaxError

# ======================================================================================================================
#
#   ####   #####   ##     ##  ######  #####  ##    ##  ######         ####  #####   ##      ##  ######
#  ##     ##   ##  ####   ##    ##    ##      ##  ##     ##          ##     ##  ##  ##      ##    ##
#  ##     ##   ##  ##  ## ##    ##    #####    ####      ##           ###   #####   ##      ##    ##
#  ##     ##   ##  ##    ###    ##    ##      ##  ##     ##             ##  ##      ##      ##    ##
#   ####   #####   ##     ##    ##    #####  ##    ##    ##          ####   ##      ######  ##    ##
#
# ======================================================================================================================


def context_split(
    string: str,
    delimiter: str = ",",
    contexts: tuple[str, ...] = (),
    escape_char: str = "\\",
    remove_empty: bool = False,
) -> tuple:
    """Split string at delimiter, except for in the middle of the specified contexts"""

    state = [0 for _ in contexts]  # States of each context
    last_break, escape, parts = 0, False, []  # Keep track of

    for si, char in enumerate(string):
        if escape:
            escape = False
            continue

        for ci, c in enumerate(contexts):
            if not any(state[ci + 1 :]):
                if state[ci]:
                    # First try to match the closing context if state is already high
                    # This make matching the same delimiter for opening and closing work
                    if char is c[1]:
                        state[ci] -= 1
                    elif char is c[0]:
                        state[ci] += 1
                else:
                    if char is c[0]:
                        state[ci] += 1
                    elif char is c[1]:
                        state[ci] -= 1

        escape = char is escape_char  # Escape the next char

        if not any(state) and (char is delimiter or not delimiter):
            parts.append(string[last_break:si])
            if delimiter:
                si += 1  # Skip delimiter
            last_break = si

        if any(s < 0 for s in state):
            raise PsllSyntaxError("Invalid context structure. Ketbra context match.")

    parts.append(string[last_break:])

    if any(state):
        raise PsllSyntaxError("Invalid context structure. Incomplete context.")

    if remove_empty:
        parts = [p for p in parts if p]

    return tuple(parts)


# =============================================================
#
#  ##      #####  ##    ##
#  ##      ##      ##  ##
#  ##      #####    ####
#  ##      ##      ##  ##
#  ######  #####  ##    ##
#
# =============================================================


def split(string: str) -> tuple:
    """Context-sensitive split for the lexer"""
    return context_split(
        string,
        delimiter=" ",
        contexts=("()", "[]", '""'),
        escape_char="\\",
        remove_empty=True,
    )


def in_context(text: str, context: str) -> bool:
    """Check if text is in the specified context"""
    return len(text) >= 2 and text[0] == context[0] and text[-1] == context[1]


def lex(text: str) -> tuple:
    """Compose a basic abstract syntax tree from the reduced source"""
    return tuple((lex(s[1:-1]) if in_context(s, "()") else s) for s in split(text))
