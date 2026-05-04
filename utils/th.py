import telethon.tl.custom.message
import typing
import utils.log


class TelethonHandler(typing.NamedTuple):
    name: str  # command name
    handler_impl: typing.Callable[[telethon.tl.custom.message.Message], typing.Awaitable[None]]

    async def invoke(self, msg: telethon.tl.custom.message.Message) -> None:
        try:
            await self.handler_impl(msg)
        except Exception:
            utils.log.get("telethon handler").exception("invoke exception")
