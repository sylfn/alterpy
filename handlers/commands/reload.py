import utils.cm
import utils.mod
import utils.ch
import utils.regex
import utils.system
import handlers.cm
import os
import sys
import PyGitUp.gitup


async def on_reload(cm: utils.cm.CommandMessage) -> None:
    res = await utils.mod.load_handlers(
        handlers.cm.initial_handlers,
        handlers.cm.ch_list,
        handlers.cm.handlers_dir,
        True
    )
    await cm.int_cur.reply(res)


async def on_shutdown(cm: utils.cm.CommandMessage) -> None:
    await cm.int_cur.reply('→ Shutting down...')
    sys.exit()


async def on_hard_reload(cm: utils.cm.CommandMessage) -> None:
    # TODO: other way/
    PyGitUp.gitup.GitUp().run()
    await cm.int_cur.reply('→ Restarting...')
    argv = utils.system.argv()
    os.execve(sys.executable, argv, {'alterpy_prev': f'{cm.sender.chat.id} {cm.id}'})


handler_list = [
    utils.ch.CommandHandler(name="reload", pattern=utils.regex.cmd(utils.regex.unite("перезапуск", "reload")), help_page='elevated', handler_impl=on_reload, is_elevated=True),
    utils.ch.CommandHandler(name="shutdown", pattern=utils.regex.cmd(utils.regex.unite("shutdown")), help_page='elevated', handler_impl=on_shutdown, is_elevated=True),
    utils.ch.CommandHandler(name="hard_reload", pattern=utils.regex.cmd(utils.regex.unite("рестарт", "reboot")), help_page='elevated', handler_impl=on_hard_reload, is_elevated=True),
]

