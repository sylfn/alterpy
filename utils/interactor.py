import telethon.tl.custom
import traceback
import typing
import utils.log

log = utils.log.get("telethon")


class MessageInteractor(typing.NamedTuple):
    message: telethon.tl.custom.message.Message

    async def reply(self, text: str, file: typing.Any = None, link_preview: bool = True) -> "typing.Optional[MessageInteractor]":
        """Reply to message"""
        try:
            return MessageInteractor(await self.message.reply(text, file=file, link_preview=link_preview))
        except Exception as e:
            try:
                await self.message.reply(f"Exception: {e}")
            except:
                pass
            log.error(f"Could not reply to t.me/{self.message.chat.id}/{self.message.id}: {repr(e)}")
        return None

    async def send_file(self, file: typing.Any, as_reply: bool = False, **kwargs: typing.Any) -> "typing.Optional[MessageInteractor]":
        """Send file with special parameters (for example as voice note)"""
        try:
            return MessageInteractor(await self.message.client.send_file(
                await self.message.get_input_chat(),
                file,
                reply_to=(self.message if as_reply else None),
                **kwargs
            ))
        except Exception as e:
            try:
                await self.message.reply(f"Exception: {e}")
            except:
                pass
            log.error(f"Could not send file to t.me/{self.message.chat.id}/{self.message.id}: {repr(e)}")
        return None
