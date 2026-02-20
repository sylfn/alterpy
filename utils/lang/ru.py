import pymorphy3
import utils.pyphrasy3
import utils.str
import utils.log
import utils.transliterator
import os.path
import typing

log = utils.log.get("lang-ru")


class NoInflectAnalyzer:
    def get_lexeme(self, parse):
        return [parse]
class NopMorph:
    def _inflect(self, parse, infl):
        return [parse]
def _make_word(word, normal_form, tag, score):
    parse = pymorphy3.analyzer.Parse(
        word = word,
        normal_form = normal_form,
        tag = morph.morph.TagClass(tag),
        score = score,
        methods_stack = (NoInflectAnalyzer(),),
    )
    parse._morph = NopMorph()
    return parse

def _gender_number(gender):
    number = 'plur' if 'plur' in gender else 'sing'
    gender = next(iter(gender - {number}), None)
    return gender, number


class MorphAnalyzer:
    __slots__ = ['morph']

    def __init__(self, morph: pymorphy3.MorphAnalyzer) -> None:
        self.morph = morph

    def patch_gender(self, parse: pymorphy3.analyzer.Parse, g) -> pymorphy3.analyzer.Parse:
        if not g: return parse
        gender, number = _gender_number(g)
        old_tag = str(parse.tag)
        tag = old_tag
        if gender: tag = tag.replace('masc', gender).replace('femn', gender).replace('neut', gender).replace('ms-f', gender).replace('GNdr', gender)
        if number: tag = tag.replace('sing', number).replace('plur', number) # .replace('Sgtm', number).replace('Pltm', number)
        tag = tag.replace(',,', ',').replace(', ', ' ').replace(' ,', ' ')
        if old_tag == tag: return parse
        return _make_word(parse.word, parse.normal_form, tag, parse.score)

    def parse(self, word: str, g = None) -> list[pymorphy3.analyzer.Parse]:
        def make_equal(x: str) -> str:
            return utils.str.equal_capitalize(x, word)

        parsed = [
            el._replace(
                word=make_equal(el.word),
                normal_form=make_equal(el.normal_form)
            )
            for el in self.morph.parse(word)
        ]
        if not g: return parsed

        # Filter by gender and if none found, pretend the word doesn't need inflections
        gender, number = _gender_number(g)
        return [
            self.patch_gender(el, g) for el in parsed
            if (gender is None or gender == el.tag.gender or 'ms-f' in el.tag or 'GNdr' in el.tag)
            # and (number == el.tag.number or 'Sgtm' in el.tag or 'Pltm' in el.tag)
            and 'nomn' == el.tag.case
        ] or [
            _make_word(word, word, f'NOUN,anim,{gender},Name {number},nomn'.replace(',,', ','), 0.1)
        ]


def parse_inflect(word: pymorphy3.analyzer.Parse, form: typing.Union[str, set[str], frozenset[str]], g = None) -> pymorphy3.analyzer.Parse:
    if type(form) == str:
        form = {form}
    # if g:
    #     gender, number = _gender_number(g)
    #     form = form | {number}
    res = word.inflect(form)
    res = res._replace(word=utils.str.equal_capitalize(res.word, word.word))
    return morph.patch_gender(res, g)


def word_inflect_parse(word: str, form: typing.Union[str, set[str], frozenset[str]], g = None) -> pymorphy3.analyzer.Parse:
    return parse_inflect(morph.parse(word, g)[0], form, g)


morph = MorphAnalyzer(pymorphy3.MorphAnalyzer())
pi = utils.pyphrasy3.PhraseInflector(morph, parse_inflect)


def merge(a: str, b: str) -> str:
    return f'{a}({b[len(os.path.commonprefix([a, b])):]})'


genders = [frozenset({'sing', 'masc'}), frozenset({'sing', 'femn'}), frozenset({'sing', 'neut'}), frozenset({'plur'})]
pn_to_g = [0, 0, 1, 2, 2, 3]

def _past(parse: pymorphy3.analyzer.Parse, i: int) -> str:
    return parse_inflect(parse, {'past'} | genders[i]).word


def past(parse: pymorphy3.analyzer.Parse, p: int) -> str:
    if p == 0: return merge(_past(parse, 0), _past(parse, 1))
    return _past(parse, pn_to_g[p])


def try_verb_past(w: str, p: int) -> str:
    parse = morph.parse(w)[0]
    tag = parse.tag
    if 'INFN' not in tag:
        return w
    return past(parse, p)


def inflect(s: str, form: typing.Union[str, set[str], frozenset[str]], p: int | None = None) -> str:
    g = p and genders[pn_to_g[p]]
    try:
        return pi.inflect(s, form, g)
    except:
        return word_inflect_parse(s, form, g).word


def agree_with_number(s: str, num: int, form: typing.Union[str, set[str], frozenset[str]]) -> str:
    ret = word_inflect_parse(s, form).make_agree_with_number(num).word
    assert isinstance(ret, str)
    return ret


translit = utils.transliterator.Transliterator()


def tr(s: str) -> str:
    return translit.inverse_transliterate(s)


def ander(arr: list[str]) -> str:
    return (', '.join(arr))[::-1].replace(' ,', ' и ', 1)[::-1]

