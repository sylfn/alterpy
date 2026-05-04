import utils.cm
import utils.rand
import utils.regex
import random


async def on_da(cm: utils.cm.CommandMessage) -> None:
    if random.randint(1, 4) == 1:
        await cm.int_cur.reply(
            utils.rand.weighted([
                (1, 'сковорода'),
                (1, 'лабуда'),
                (1, 'винда'),
            ])
        )


async def on_net(cm: utils.cm.CommandMessage) -> None:
    if random.randint(1, 4) == 1:
        await cm.int_cur.reply(
            utils.rand.weighted([
                (1, 'солнышка ответ'),
                (1, 'лунышка ответ'),
            ])
        )


async def on_dura(cm: utils.cm.CommandMessage) -> None:
    if random.randint(1, 4) == 1:
        await cm.int_cur.reply('а может ты 🤨?')


async def on_spok(cm: utils.cm.CommandMessage) -> None:
    await cm.int_cur.reply('Cладких снов 🥺')


handler_list = [
    utils.cm.CommandHandler(name=name, pattern=utils.regex.raw(pat), help_page="kek", handler_impl=handler)
    for name, pat, handler in [
        ("да", "\\bда$", on_da),
        ("нет", "\\bнет$", on_net),
        ("дура", "\\bдура$", on_dura),
        ("спокойной ночи", "^((всем ){0,1}спокойной ночи)", on_spok),
    ]
]

