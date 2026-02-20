# https://github.com/summerisgone/pyphrasy

from collections import defaultdict
from operator import attrgetter
import utils.log
import utils.regex
import pymorphy3
import typing


GRAM_CHOICES = ('nomn', 'gent', 'datv', 'accs', 'ablt', 'loct', 'voct', 'gen2', 'acc2', 'loc2', 'sing', 'plur')

logger = utils.log.get("pyphrasy3")


class InflectionError(Exception):
    pass


class PhraseInflector(object):
    class ScoreHelper(object):
        score = 0
        fixed_number_score = 0

        def __init__(self, parsed: pymorphy3.analyzer.Parse) -> None:
            self.parsed = parsed

    def __init__(self, morph: pymorphy3.MorphAnalyzer, inf: typing.Callable[[pymorphy3.analyzer.Parse, typing.Union[str, set[str], frozenset[str]]], pymorphy3.analyzer.Parse]) -> None:
        self.morph = morph
        self.inf = inf

    def parse_first(self, word: str) -> typing.Optional[pymorphy3.analyzer.Parse]:
        parse = self.morph.parse(word)
        if len(parse) > 0:
            return parse[0]
        else:
            return None

    def select_master(self, phrase: list[str], g = None) -> typing.Optional[ScoreHelper]:
        versions = []
        for i, word in enumerate(phrase):
            forms = defaultdict(list)
            # If a word identified as noun may also be identified as participle, adjective or adjective
            # it is less likely to be a real noun
            is_derivative = any({'ADJF', 'PRTF', 'GRND'} & version.tag.grammemes for version in self.morph.parse(word))

            for j, parsed in enumerate(self.morph.parse(word)):
                if {'NOUN', 'nomn'} in parsed.tag:
                    version = self.ScoreHelper(parsed)
                    version.fixed_number_score = 1 if ({'Pltm', 'Sgtm'} & set(parsed.tag.grammemes)) else 0
                    version.score = (100.0 * parsed.score / (1.0 + 0.2 * j + (1 if is_derivative else 0))
                                     + 20 / (0.2 * i + 1))
                    forms[parsed.score].append(version)
            # all other things being equal, fixed number forms will score better
            forms_pass = [max(x, key=attrgetter('fixed_number_score')) for x in forms.values()]
            versions.extend(forms_pass)

        if versions:
            master = sorted(versions, key=attrgetter('score'), reverse=True)[0]
            master.parsed = self.morph.patch_gender(master.parsed, g)
            return master
        else:
            return None

    def inflect(self, phrase: str, form: typing.Union[str, set[str], frozenset[str]], g = None) -> str:
        master_word = self.select_master(utils.regex.split_by_word_border(phrase), g)
        if master_word:
            return self._inflect_with_master(form, phrase, master_word.parsed, g)
        else:
            # logger.error('Can not find master word in: {0}'.format(phrase))
            return self._inflect_without_master(form, phrase)

    def _inflect_with_master(self, form: typing.Union[str, set[str], frozenset[str]], phrase: str, master_word: pymorphy3.analyzer.Parse, g) -> str:
        result = []
        if isinstance(form, str):
            form = {form}
        else:
            form = set(form)
        # Do not inflect in numbers if master word is always plur or sing
        if {'Pltm', 'Sgtm'} & set(master_word.tag.grammemes):
            form = form - {'sing', 'plur'}

        infl = form
        inflected_master = self.inf(master_word, infl, g)  # master_word.inflect(infl)
        if not inflected_master:
            logger.error('Can not inflect master word {1} with {2}: {0}'.format(phrase, master_word.word, str(infl)))

        for chunk in utils.regex.split_by_word_border(phrase):
            parsed_chunk = self.morph.parse(chunk)
            if chunk.lower() == master_word.word.lower():
                if inflected_master:
                    result.append(inflected_master.word)
                else:
                    result.append(chunk)
                continue

            dependent = None
            for version in parsed_chunk:
                # If POS should adopt the form AND was in the same case(падеж) which the master word had
                if version.tag.POS in ('ADJF', 'PRTF') and version.tag.case == master_word.tag.case:
                    infl = form | {inflected_master.tag.number}
                    # If in the single number, adopt the gender of master word
                    if inflected_master.tag.number == 'sing':
                        infl.add(inflected_master.tag.gender)

                    if ('accs' in form) \
                            and (inflected_master.tag.gender == 'masc' or inflected_master.tag.number == 'plur'):
                        infl.add(master_word.tag.animacy)

                    try:
                        inflected = self.inf(version, infl)  # version.inflect(infl)
                    except ValueError as e:
                        logger.error('{0} at {1}'.format(e, version.word))
                        dependent = version
                    else:
                        if inflected:
                            dependent = inflected
                        else:
                            logger.error('Can not inflect word {1} with {2}: {0}'.format(phrase, version.word, infl))
                            dependent = version
                    break

            if dependent:
                result.append(dependent.word)
            else:
                result.append(chunk)

        return ''.join(result)

    def _inflect_without_master(self, form: typing.Union[str, set[str], frozenset[str]], phrase: str) -> str:
        result = []
        if isinstance(form, str):
            form = {form}
        else:
            form = set(form)
        for chunk in utils.regex.split_by_word_border(phrase):
            parsed_chunk = self.parse_first(chunk)
            if not parsed_chunk:
                result.append(chunk)
                continue
            if not any(form in parsed_chunk.tag for form in ({'NOUN', 'nomn'}, {'ADJF', 'nomn'})):
                result.append(chunk)
                continue
            infl = form
            if 'accs' in form:
                infl.add('inan')
            try:
                inflected = self.inf(parsed_chunk, infl)  # parsed_chunk.inflect(infl)
                if inflected:
                    result.append(inflected.word)
                else:
                    logger.error('Can not inflect word {1}: {0}'.format(phrase, chunk))
                    result.append(chunk)
            except ValueError:
                result.append(chunk)

        return ''.join(result)

