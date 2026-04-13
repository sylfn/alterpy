import utils.file
import utils.cm
import utils.ch
import utils.regex
import utils.str
import typing
import re


def entry(lang: str, path: str = '', name: str = '') -> str:
    return (f'https://yuki0iq.github.io/alterpy/{path}{lang}#{name}').replace('\\', '\\\\').replace(')', '\\)')


def link(lang: str, path: str = '', name: str = '') -> str:
    ent = entry(lang, path, name)
    return f'[{utils.str.escape(name or "Help")}]({ent})'


def forward_handler(path: str) -> typing.Callable[[utils.cm.CommandMessage], typing.Awaitable[None]]:
    async def on_help(cm: utils.cm.CommandMessage) -> None:
        # TODO add check exists.
        await cm.int_cur.reply(link(cm.lang, path, cm.arg))
    return on_help


def on_reverse_help_impl(handlers: list[typing.Any], arg: str, help_cmds: list[str], path: str, lang: str) -> str:
    if not arg:
        return f"Type `{help_cmds} [command]` to view help page for command"

    help_pages_list = [
        handler.help_page
        for handler in filter(
            lambda handler:
                bool(re.search(handler.pattern, arg)),
            handlers
        )
    ]

    if not help_pages_list:
        return f"Could not match `{arg}`"

    res = "Help entries:\n" + '\n'.join(map(lambda x: link(lang, path, x), help_pages_list))
    print(res)
    return res


def reverse_handler(handlers: list[typing.Any], help_cmds: list[str], path: str) -> typing.Callable[[utils.cm.CommandMessage], typing.Awaitable[None]]:
    async def on_help(cm: utils.cm.CommandMessage) -> None:
        await cm.int_cur.reply(on_reverse_help_impl(handlers, cm.arg, help_cmds, path, cm.lang))
    return on_help


def add(handlers: list[typing.Any], man_cmds: list[str] = ["man"], help_cmds: list[str] = ["help"], path: str = "") -> None:
    if path:
        path += '_'
    help_page = 'help'
    handlers.extend([
        utils.ch.CommandHandler(name=name, pattern=utils.regex.pre(utils.regex.union(commands)), help_page=help_page, handler_impl=handler, is_prefix=True, is_arg_current=True)
        for name, commands, handler in [
            (f'man{path}',  man_cmds,  forward_handler(path)),
            (f'help{path}', help_cmds, reverse_handler(handlers, help_cmds, path))
        ]
    ])

