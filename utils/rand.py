import typing
import random


def rand_or_null_fun(s: str, p: int, q: int, s2: str = "") -> typing.Callable[[], str]:
    return lambda: (s if random.randint(1, q) <= p else s2)


def weighted(pairs: list[tuple[int, typing.Any]]) -> typing.Any:
    """
    https://stackoverflow.com/a/14992648
    """
    total = sum(pair[0] for pair in pairs)
    r = random.randint(1, total)
    for (weight, value) in pairs:
        r -= weight
        if r <= 0:
            return value


def printable(n: int = 10, chars: str = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890") -> str:
    return ''.join(random.choice(chars) for _ in range(n))

