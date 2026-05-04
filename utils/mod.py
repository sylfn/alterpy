import asyncio
import utils.log
import utils.file
import importlib
import typing

log = utils.log.get("modloader")


async def load_handlers_from_name(name: str, do_reload: bool) -> tuple[bool, list[typing.Any]]:
    try:
        mod = importlib.import_module(name)
        if do_reload:
            mod = importlib.reload(mod)
            if hasattr(mod, 'init'):
                await mod.init()
        handlers = mod.handler_list
        log.info(f"Loaded [italic]{name}[/] [green bold]OK[/]!")
        return True, handlers
    except:
        log.exception(f"[red]Failed[/] to load handlers from [italic]{name}[/], ignoring module")
        return False, []


async def load_handlers_from_filename(filename: str, do_reload: bool) -> tuple[bool, list[typing.Any]]:
    return await load_handlers_from_name(filename[:-3].replace('/', '.'), do_reload)


async def load_handlers(initial_handlers: list[typing.Any], handlers: list[typing.Any], path: str, do_reload: bool = False) -> str:
    """
    load all .py files from given path and merge all of their "handlers" into given with initial
    returns log message
    """

    if path[-1] != '/':
        path = path + '/'
    path = path.replace('\\', '/')

    log.info(f"Started loading from ./{path}")

    handlers[:] = initial_handlers[:]
    filenames = list(filter(lambda fn: fn[-3:] == ".py" and '__' not in fn, sorted(utils.file.list_filenames(path))))

    cnt_ok, cnt = 0, len(filenames)

    loaders = [load_handlers_from_filename(filename, do_reload) for filename in filenames]
    for loader in asyncio.as_completed(loaders):
        ok, cur_handlers = await loader
        cnt_ok += int(ok)
        handlers.extend(cur_handlers)

    log.info(f"Loading from ./{path} finished, {cnt_ok} of {cnt} loaded successfully")

    return f"{cnt_ok} of {cnt} loaded successfully"

