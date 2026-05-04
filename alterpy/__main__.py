import asyncio
import rich.console
import rich.traceback
import sqlite3
import sys
import utils.log

from . import core


log = utils.log.get("main")

rich.traceback.install(show_locals=True)

try:
    asyncio.run(core.main(log))
except sqlite3.OperationalError:
    log.error("Another instance of this bot is already running!")
except KeyboardInterrupt:
    log.info("Stopping... [KeyboardInterrupt]")
except SystemExit:
    log.info("Shutting down...")
