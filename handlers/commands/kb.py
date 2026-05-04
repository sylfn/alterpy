import utils.regex
import utils.str
import utils.cm
import utils.ch
import utils.locale
import utils.common

handler_list = []


async def on_layout(cm: utils.cm.CommandMessage) -> None:
    if cm.arg:
        await cm.int_cur.reply(utils.str.escape(utils.str.change_layout(cm.arg)))


async def on_me(cm: utils.cm.CommandMessage) -> None:
    if cm.arg:
        msg = f"\\* _{cm.sender.get_display_name()} {utils.str.escape(cm.arg)}_"
        if cm.int_prev:
            await cm.int_prev.reply(msg)
        else:
            await cm.int_cur.respond(msg)
        try:
            await cm.int_cur.delete()
        except:
            await cm.int_cur.reply("Can't delete message — no permission")


handler_list.append(utils.ch.CommandHandler(
    name='layout',
    pattern=utils.regex.cmd(utils.regex.unite('kb', 'ли', 'layout', 'дфнщге', 'раскладка', 'hfcrkflrf', 'рас', 'hfc')),
    help_page="keyboard",
    handler_impl=on_layout,
    is_prefix=True
))

handler_list.append(utils.ch.CommandHandler(
    name="me",
    pattern=utils.regex.pre(utils.regex.unite('me', 'я')),
    help_page='me',
    handler_impl=on_me,
    is_prefix=True
))
