import utils.command
import utils.regex


async def on_repeat(cm: utils.command.Message) -> None:
    if cm.int_prev:
        msg_prev = cm.int_prev.message
        cm_new = await utils.command.from_message(msg_prev)
        cm_new = cm_new._replace(sender=cm.sender)._replace(time=cm.time)._replace(local_time=cm.local_time)  # <- for rights, and other
        await utils.command.process_command_message(cm_new)


handler_list = [utils.command.Handler(
    name="repeat",
    pattern=utils.regex.cmd(utils.regex.unite("повтор", "заново", "repeat")),
    help_page="repeat",
    handler_impl=on_repeat
)]
