import random
import re
import typing

import utils.regex
import utils.locale


any_pronouns_regex = utils.regex.ignore_case(utils.regex.union('any люб'.split()))

pronouns_regex = {
    0: utils.regex.ignore_case(utils.regex.union('0 vo nul no нет избег'.split())),
    1: utils.regex.ignore_case(utils.regex.unite(
        *'1 him boy mas его па му тот мас'.split(),
        utils.regex.negative_lookbehind('fe') + 'mal',
        utils.regex.negative_lookbehind('wo') + 'man',
        utils.regex.unite(
            utils.regex.word_border() + 'he',
            'он'
        ) + utils.regex.word_border()
    )),
    2: utils.regex.ignore_case(utils.regex.union('2 she her wom gir fem она её ее де же та фем'.split())),
    3: utils.regex.ignore_case(utils.regex.union('3 it'.split())),
    4: utils.regex.ignore_case(utils.regex.unite(
        *'4 one neu оно'.split(),
        'то' + utils.regex.negative_lookahead('т')
    )),
    5: utils.regex.ignore_case(utils.regex.union('5 the они их эти те'.split())),
}

pronouns_name = {
    'list': {'ru': 'любые из', 'en': 'any of'},
    -1: {'ru': 'любые', 'en': 'any'},
    0: {'ru': 'не используются', 'en': 'null'},
    1: {'ru': 'он/его', 'en': 'he/his'},
    2: {'ru': 'она/её', 'en': 'she/her'},
    3: {'ru': 'оно/его', 'en': 'it/its'},
    4: {'ru': 'нейтральное оно', 'en': 'one/one\'s'},
    5: {'ru': 'они/их', 'en': 'singular they'},
}
pronouns_name[None] = pronouns_name[0]
pronouns_name_getter = utils.locale.Localizator(pronouns_name)


def to_str(pns: None | list[int], lang: str = "ru") -> str:
    if pns is None or len(pns) == 1:
        pns = pns and pns[0]
        return pronouns_name_getter.obj(pns, lang)
    return pronouns_name_getter.obj('list', lang) + ' ' + ', '.join(pronouns_name_getter.obj(pn, lang) for pn in pns)


def from_str(s: str) -> None | list[int]:
    if re.search(any_pronouns_regex, s):
        return [-1]
    ans = []
    for pn, pat in pronouns_regex.items():
        if re.search(pat, s):
            ans.append(pn)
    if not ans:
        return None
    return ans


def to_int(pns: None | int | list[int]) -> int:
    if pns is None:
        return 0
    if pns == -1:
        return random.randint(0, 5)
    if isinstance(pns, int):
        return pns
    return random.choice(pns)


if __name__ == '__main__':
    # todo more tests?
    assert(from_str('any') == -1)
    assert(from_str('null') == 0)
    assert(from_str('она/они') == [2, 5])
    assert(from_str('он') == 1)
    assert(from_str('оно') == 4)
    assert(from_str('one/one\'s') == 4)
