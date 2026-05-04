import utils.command
import utils.regex
import utils.locale

import random
import re

handler_list = []

translations = {
    'prefs': {
        'en': [
            "Yuki said",
            "Our Government thinks",
            "Cats selected",
            "I was forced to say",
            "Ryijik meowed",
            "You'd like to hear"
        ],
        'ru': [
            "Звёзды говорят",
            "Юки сказала",
            "Правительство нашептало",
            "Карты таро передали",
            "Котики выбрали",
            "Меня заставили сказать",
            "Осинка мяукнула",
            "Я знаю, что ты хочешь услышать",
            "Проверяй,",
            "Ставлю сотку,",
            "Древние оракулы выбрали",
            "Пусть будет",
            "Как знать,",
            "Рандом выбрал",
            "Я выбрала",
            "Сова выбрала",
            "Разрабам альтерпая нефиг делать и они решили",
            "Питон передаёт",
            "Справедливый выбор —",
            "Птичка нашептала"
        ],
    },
}

LOC = utils.locale.Localizator(translations)


async def on_prob(cm: utils.command.Message) -> None:
    pref = random.choice(LOC.obj('prefs', cm.lang))
    val = random.randint(0, 100)
    await cm.int_cur.reply(f"{pref} {val}%")


async def on_choose(cm: utils.command.Message) -> None:
    opts = re.split('(?i)(^|\\s)(or|или)($|\\s)', cm.arg)[::4]
    pref = random.choice(LOC.obj('prefs', cm.lang))
    val = random.choice(opts).strip()
    await cm.int_cur.reply(f"{pref} {val}")


handler_list.append(utils.command.Handler(
    name='prob',
    pattern=utils.regex.cmd(utils.regex.unite('prob', 'chance', 'инфа', 'шанс', 'вер', 'вероятность')),
    help_page="random",
    handler_impl=on_prob
))

handler_list.append(utils.command.Handler(
    name='choose',
    pattern=utils.regex.cmd(utils.regex.unite('choose', 'select', 'выбери')),
    help_page="random",
    handler_impl=on_choose,
    is_prefix=True
))
