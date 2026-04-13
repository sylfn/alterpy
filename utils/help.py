import utils.file
import utils.cm
import utils.ch
import utils.regex
import utils.str
import typing
import re


def entry(name: str) -> str:
    return (f'https://sylfn.github.io/alterpy/help#{name}').replace('\\', '\\\\').replace(')', '\\)')


def link(name: str) -> str:
    if name and name not in "start ping keyboard random me tts kek calend elevated repeat rp2 rp3 pronouns redirect lang help".split():
        return f'(раздел {name} ещё не написан)'
    return f'[{utils.str.escape(name or "Справка")}]({entry(name)})'


def forward_handler() -> typing.Callable[[utils.cm.CommandMessage], typing.Awaitable[None]]:
    async def on_help(cm: utils.cm.CommandMessage) -> None:
        await cm.int_cur.reply(link(cm.arg))
    return on_help


def on_reverse_help_impl(handlers: list[typing.Any], arg: str, help_cmds: list[str]) -> str:
    if not arg:
        return f"Набери `{help_cmds} [команда]`, чтобы увидеть справку по конкретной команде, например `{help_cmds} +мест`"

    help_pages_list = [
        handler.help_page
        for handler in filter(
            lambda handler:
                bool(re.search(handler.pattern, arg)),
            handlers
        )
    ]

    if not help_pages_list:
        return f"Нет справки по команде `{arg}`"

    res = "Найденные разделы:\n" + '\n'.join(map(lambda x: link(lang, x), help_pages_list))
    print(res)
    return res


def reverse_handler(handlers: list[typing.Any], help_cmds: list[str]) -> typing.Callable[[utils.cm.CommandMessage], typing.Awaitable[None]]:
    async def on_help(cm: utils.cm.CommandMessage) -> None:
        await cm.int_cur.reply(on_reverse_help_impl(handlers, cm.arg, help_cmds))
    return on_help


def add(handlers: list[typing.Any], man_cmds: list[str] = ["man"], help_cmds: list[str] = ["help"]) -> None:
    handlers.extend([
        utils.ch.CommandHandler(
            name=name,
            pattern=utils.regex.pre(utils.regex.union(commands)),
            help_page='help',
            handler_impl=handler,
            is_prefix=True,
            is_arg_current=True
        )
        for name, commands, handler in [
            (f'man',  man_cmds,  forward_handler()),
            (f'help', help_cmds, reverse_handler(handlers, help_cmds))
        ]
    ])

