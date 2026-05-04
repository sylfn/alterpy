import utils.cm
import utils.log
import utils.regex
import utils.media

import typing
import re
import inspect


class CommandHandler(typing.NamedTuple):
    name: str  # command name
    pattern: re.Pattern[str]  # regex pattern
    help_page: str
    handler_impl: typing.Callable[[utils.cm.CommandMessage], typing.Awaitable[None]]
    is_prefix: bool = False  # should a command be deleted from its message when passed to handler
    is_elevated: bool = False  # should a command be invoked only if user is admin
    is_arg_current: bool = False  # don't take arg from reply if set

    async def invoke(self, cm: utils.cm.CommandMessage) -> None:
        if not self.is_elevated or cm.sender.is_admin():
            try:
                await self.handler_impl(cm)
            except Exception as e:
                await cm.int_cur.reply(f"Exception: {e}")
                utils.log.get("handler").exception("invoke exception")
        else:
            await cm.int_cur.reply("Only bot admins can run elevated commands")


def apply(cm: utils.cm.CommandMessage, ch: CommandHandler) -> utils.cm.CommandMessage:
    arg = re.sub(ch.pattern, '', cm.arg)
    if not len(arg) and not ch.is_arg_current:
        arg = cm.rep
    if not cm.msg.media and not ch.is_arg_current:
        cm = cm._replace(media=cm.reply_media)
    return cm._replace(arg=arg)

