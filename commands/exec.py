import utils.command
import utils.regex
import typing
import traceback  # TODO fix!


async def on_exec(cm: utils.command.Message) -> None:
    shifted_arg = cm.arg.strip().strip('`').replace('\n', '\n    ')
    code = '\n'.join([
        f"async def func():",
        f"    {shifted_arg}",
    ])
    try:
        code_locals: dict[str, typing.Any] = dict()
        exec(code, globals() | locals(), code_locals)
        await code_locals['func']()
    except:
        await cm.int_cur.reply(f"```{traceback.format_exc()}```")
        code_lines = code.split('\n')
        lined_code = '\n'.join(f"{i+1:02}  {code_lines[i]}" for i in range(len(code_lines)))
        await cm.int_cur.reply(f"While executing following code:\n```{lined_code}```")


handler_list = [utils.command.Handler(
    name="exec",
    pattern=utils.regex.cmd("exec"),
    help_page='elevated',
    handler_impl=on_exec,
    is_prefix=True,
    is_elevated=True
)]
