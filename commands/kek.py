import utils.command
import utils.regex

async def on_spok(cm: utils.command.Message) -> None:
    await cm.int_cur.reply('Cладких снов 🥺')

handler_list = [
    utils.command.Handler(name="спокойной ночи", pattern=utils.regex.raw("((всем ){0,1}спокойной ночи)"), help_page="kek", handler_impl=on_spok)
]
