import utils.log
import utils.user
import utils.interactor
import alterpy.context

import asyncio
import datetime
import re
import typing
import telethon.tl.custom
import telethon.tl.types
import telethon.client

class Message(typing.NamedTuple):
    arg: str  # message text
    rep: str  # message text with reply attached
    time: datetime.datetime  # UTC time when sent
    local_time: datetime.datetime  # UTC time when recv
    sender: utils.user.User  # sender
    reply_sender: typing.Optional[utils.user.User]  # reply sender if applicable
    int_cur: utils.interactor.MessageInteractor  # for current message
    int_prev: typing.Optional[utils.interactor.MessageInteractor]  # for attached reply
    client: telethon.client.telegramclient.TelegramClient
    id: int
    reply_id: int  # -1 if no reply
    msg: telethon.tl.custom.message.Message
    lang: str

class Handler(typing.NamedTuple):
    name: str  # command name
    pattern: re.Pattern[str]  # regex pattern
    help_page: str
    handler_impl: typing.Callable[[Message], typing.Awaitable[None]]
    is_prefix: bool = False  # should a command be deleted from its message when passed to handler
    is_elevated: bool = False  # should a command be invoked only if user is admin
    is_arg_current: bool = False  # don't take arg from reply if set

    async def invoke(self, cm: Message) -> None:
        if not self.is_elevated or cm.sender.is_admin():
            try:
                await self.handler_impl(cm)
            except Exception as e:
                await cm.int_cur.reply(f"Exception: {e}")
                utils.log.get("handler").exception("invoke exception")
        else:
            await cm.int_cur.reply("Only bot admins can run elevated commands")

handlers: list[Handler] = []
initial: list[Handler] = []
location = "commands"

def apply(cm: Message, ch: Handler) -> Message:
    arg = re.sub(ch.pattern, '', cm.arg)
    if not len(arg) and not ch.is_arg_current:
        arg = cm.rep
    return cm._replace(arg=arg)

async def from_message(msg_cur: telethon.tl.custom.message.Message) -> Message:
    msg_prev = await msg_cur.get_reply_message()
    has_reply = msg_prev is not None
    chat_obj = await msg_cur.get_chat()

    client = msg_cur.client
    id = msg_cur.id
    reply_id = msg_prev.id if msg_prev else -1

    # TODO handle markdownv2 properly
    def unmd2(s: typing.Optional[str], es: list[typing.Any]) -> str:
        if not s: return ""
        s = s.replace('\\_', '_').replace('\\(', '(').replace('\\)', ')').replace('\\|', '|')
        mentions = []
        for e in es or []:
            if isinstance(e, telethon.tl.types.MessageEntityMentionName):
                i, l, uid = e.offset, e.length, e.user_id
                mentions.append((-i, i, l, uid))
        for k, i, l, uid in sorted(mentions):
            s = s[:i] + '{' + str(uid) + '|' + str(l) + '}' + s[i:]
        return s

    # .text? .message?
    arg = unmd2(msg_cur.message, msg_cur.entities)
    rep = unmd2(msg_prev.message, msg_prev.entities) if has_reply and msg_prev.message else None

    time = msg_cur.date

    sender = await utils.user.from_telethon(await msg_cur.get_sender(), chat_obj, client)
    reply_sender = await utils.user.from_telethon(await msg_prev.get_sender(), chat_obj, client) if has_reply else None

    lang = sender.get_lang()

    # self.chat = Chat(??)
    int_cur = utils.interactor.MessageInteractor(msg_cur)
    int_prev = utils.interactor.MessageInteractor(msg_prev) if has_reply else None

    local_time = datetime.datetime.now(datetime.timezone.utc)

    return Message(arg or '', rep or '', time, local_time, sender, reply_sender, int_cur, int_prev, client, id, reply_id, msg_cur, lang)

async def from_event(event: telethon.events.NewMessage) -> Message:
    return await from_message(event.message)

async def process_command_message(cm: Message) -> None:
    await asyncio.gather(*[
        handler.invoke(apply(cm, handler) if handler.is_prefix else cm)
        for handler in handlers
        if re.search(handler.pattern, cm.arg)
    ])

async def on_command_message(msg: telethon.tl.custom.message.Message) -> None:
    if msg.sender_id == alterpy.context.the_bot_id:  # Ignore messages from self
        return
    if msg.fwd_from is not None:  # Ignore forwarded messages
        return

    cm = await from_message(msg)
    await process_command_message(cm)

async def event_handler(event: telethon.events.newmessage.NewMessage) -> None:
    await on_command_message(event.message)
