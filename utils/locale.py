import utils.lang.en
import utils.lang.none
import utils.lang.ru
import utils.str
import typing


class Localizator:
    __slots__ = ['d']

    def __init__(self, d: dict[typing.Any, typing.Any]) -> None:
        self.d = d

    def obj(self, s: typing.Any, lang: str) -> typing.Any:
        if s not in self.d:
            return None
        cur = self.d[s]
        if type(cur) == str:
            return cur
        if not cur:
            return None
        if lang in cur:
            return cur[lang]
        if 'ru' in cur:
            return cur['ru']
        return list(cur.values())[0]

    def get(self, s: str, lang: str) -> str:
        return str(utils.str.FStr(self.obj(s, lang)))


langs = {
    'ru': utils.lang.ru,
    'en': utils.lang.en,
    None: utils.lang.none,
}


def lang(lg: str | None) -> typing.Any:
    return langs.get(lg)


def detect(s: str) -> str:
    if not s:
        return None

    i = 0
    while i < len(s) and not s[i].isalpha():
        i += 1

    if 'а' <= s[0].lower() <= 'я': return 'ru'
    if 'a' <= s[0].lower() <= 'z': return 'en'
    return 'ru' # unknown


def try_verb_past(w: str, p: int) -> str:
    ret = lang(detect(w)).try_verb_past(w, p)
    assert isinstance(ret, str)
    return ret

