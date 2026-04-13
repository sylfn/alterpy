import alterpy.context
import asyncio
import re
import telethon.tl.custom.message
import typing
import utils.aiospeller
import utils.ch
import utils.ch
import utils.cm
import utils.help
import utils.log
import utils.mod
import utils.th


the_bot_id = alterpy.context.the_bot_id
ch_list: list[utils.ch.CommandHandler] = []

utils.help.add(ch_list, ['man', 'ман'], ['help', 'command', 'справка', 'команда'])

initial_handlers = ch_list[:]
handlers_dir = "handlers/commands"

log = utils.log.get("cm")


async def init() -> None:
    await utils.mod.load_handlers(initial_handlers, ch_list, handlers_dir, True)


async def process_command_message(cm: utils.cm.CommandMessage) -> None:
    media_type = cm.media.type()
    # TODO fix prefix commands...
    # fixed_arg = await utils.aiospeller.correct(alterpy.context.session, cm.arg)
    fixed_arg = cm.arg  # FIXME
    await asyncio.gather(*[
        handler.invoke(
            utils.ch.apply(cm, handler) if handler.is_prefix else cm
        )
        for handler in filter(
            lambda handler:
            bool(re.search(handler.pattern, fixed_arg))
                and (media_type in handler.required_media_type
                     or not handler.required_media_type),
            ch_list
        )
    ])


async def on_command_message(msg: telethon.tl.custom.message.Message) -> None:
    if msg.sender_id == the_bot_id:  # Ignore messages from self
        return
    if msg.fwd_from is not None:  # Ignore forwarded messages
        return

    cm = await utils.cm.from_message(msg)
    await process_command_message(cm)


handler_list = [utils.th.TelethonHandler("command-message", on_command_message)]
