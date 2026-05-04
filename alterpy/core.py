import utils.command
import utils.config
import utils.help
import utils.log
import utils.mod
import sqlite3
import aiohttp
import telethon.events.newmessage
import telethon.tl.custom.message
import logging
import re
import os

from . import context

async def main(log: logging.Logger) -> None:
    log.info("AlterPy")

    config = utils.config.load("config")
    for el in config["admins"]: context.admins.add(el)
    log_id = config.get("log", 0)
    del config
    del el
    log.info("loaded config")

    alterpy_prev = os.getenv('alterpy_prev', '')
    try:
        _chat, _reply = map(int, alterpy_prev.split())
    except:
        _chat, _reply = log_id, None

    telethon_config = utils.config.load("telethon")
    try:
        async with aiohttp.ClientSession() as context.session:
            client = telethon.TelegramClient("alterpy", telethon_config['api_id'], telethon_config['api_hash'])
            await client.start(bot_token=telethon_config['bot_token'])
            async with client:
                log.info("Started telethon instance")
                if log_id:
                    try:
                        await client.send_message(_chat, "← alterpy is starting...", reply_to=_reply)
                    except:
                        log.warning("Could not reply back 'is starting'")

                context.the_bot_id = int(telethon_config['bot_token'].split(':')[0])
                del telethon_config

                utils.help.add(utils.command.handlers, ['man', 'ман'], ['help', 'command', 'справка', 'команда'])
                utils.command.initial = utils.command.handlers[:]

                res = await utils.mod.load_handlers(utils.command.initial, utils.command.handlers, utils.command.location, True)
                try:
                    await client.send_message(_chat, f"← alterpy start: {res}. Check logs for further info", reply_to=_reply)
                except:
                    log.warning("Could not reply back 'started'")

                client.add_event_handler(utils.command.event_handler, telethon.events.newmessage.NewMessage)

                log.info("Started!")
                await client.run_until_disconnected()
    except sqlite3.OperationalError:
        log.error("Another instance of this bot is already running!")
    except SystemExit:
        raise


