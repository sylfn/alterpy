import unicodedata
import utils.common
import urllib.parse


def equal_capitalize(word: str, pattern: str) -> str:
    def pat(idx: int) -> bool:
        if idx >= len(pattern):
            return pattern[-1].islower()
        return pattern[idx].islower()

    words = list(word)
    for i in range(len(words)):
        words[i] = words[i].lower() if pat(i) else words[i].upper()
    return ''.join(words)


class FStr:
    __slots__ = ['_s']

    def __init__(self, s: str) -> None:
        self._s = s

    # Actual return value is `str`
    def __repr__(self) -> any:
        return eval(str(self))

    def __str__(self) -> str:
        return f"""f'''{self._s}'''"""


def escape(s: str) -> str:
    return s.replace('\\', '\\\\').replace('_', r'\_').replace('~', r'\~').replace('[', r'\[').replace(']', r'\]').replace('*', r'\*').replace('`', r'\`')
