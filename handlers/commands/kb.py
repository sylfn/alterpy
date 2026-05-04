import utils.regex
import utils.str
import utils.cm
import utils.ch
import utils.locale
import utils.common

handler_list = []


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
    name="me",
    pattern=utils.regex.pre(utils.regex.unite('me', 'я')),
    help_page='me',
    handler_impl=on_me,
    is_prefix=True
))
