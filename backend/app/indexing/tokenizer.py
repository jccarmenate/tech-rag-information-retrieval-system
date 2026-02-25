import re

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-_+#.][a-z0-9]+)*")

_STOPWORDS = frozenset(
    """
    a an the of and or but if then else for to in on at by with from as is are was were be
    been being this that these those it its it's i you he she we they what which who whom
    will would shall should can could may might must not no nor do does did doing have has
    had having about into over under again further here there when where why how all any
    both each few more most other some such only own same so than too very s t just don
    """.split()
)


def tokenize(text: str) -> list[str]:
    """Lowercases, extracts alphanumeric tokens and drops English stopwords."""
    tokens = _TOKEN_RE.findall(text.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]
