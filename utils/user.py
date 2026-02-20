import alterpy.context
import dataclasses
import datetime
import io
import PIL.Image
import re
import sqlite3
import telethon.tl.types
import telethon.utils
import utils.common
import utils.log
import utils.str
import utils.regex


con = sqlite3.connect("users.db", autocommit=True)
cur = con.cursor()
cur.execute("PRAGMA journal_mode=WAL")
cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER, name TEXT, pronoun_set TEXT, lang TEXT, replace_id INTEGER, stamp INTEGER)")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_id ON users(id)")
cur.execute("CREATE TABLE IF NOT EXISTS chats(id INTEGER, name TEXT, stamp INTEGER)")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS chats_id ON chats(id)")
cur.execute("CREATE TABLE IF NOT EXISTS encounters(chat_id INTEGER, user_id INTEGER, stamp INTEGER)")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS encounters_chat_user_stamp on encounters(chat_id, user_id, stamp)")


def user_count() -> int:
    return cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]

def chat_count() -> int:
    return cur.execute("SELECT COUNT(*) FROM chats").fetchone()[0]


@dataclasses.dataclass
class User:
    sender: telethon.tl.types.User | telethon.tl.types.Channel | telethon.tl.types.Chat
    chat: telethon.tl.types.User | telethon.tl.types.Channel | telethon.tl.types.Chat
    client: telethon.client.telegramclient.TelegramClient

    def __post_init__(self):
        user_id = self.sender.id
        chat_id = self.chat.id
        stamp = utils.common.stamp()

        if cur.execute("SELECT COUNT(*) FROM users WHERE id = ?", (user_id,)).fetchone() == (0,):
            cur.execute("INSERT INTO users VALUES (?, NULL, NULL, NULL, NULL, 0)", (user_id,))

        encountered_time, = cur.execute("SELECT MAX(stamp) FROM encounters WHERE chat_id = ? AND user_id = ?", (chat_id, user_id)).fetchone()
        if not encountered_time or stamp - encountered_time > 7_200_000_000:
            cur.execute("INSERT INTO encounters VALUES (?, ?, ?)", (chat_id, user_id, stamp))

        chat_name = self.get_telethon_name(self.chat)
        try:
            cur.execute("INSERT INTO chats VALUES (?, ?, ?)", (chat_id, chat_name, stamp))
        except sqlite3.IntegrityError:
            cur.execute("UPDATE chats SET name = ?, stamp = ? WHERE id = ?", (chat_name, stamp, chat_id))

    def is_admin(self) -> bool:  # check if in admins list
        return self.sender.id in alterpy.context.admins

    def get_telethon_name(self, whom=None) -> str:
        if whom is None:
            whom = self.sender
        if isinstance(whom, telethon.tl.types.Channel):
            return str(whom.title)
        if not isinstance(whom, telethon.tl.types.Chat):
            return str(whom.first_name)
        return 'null'

    def get_display_name(self) -> str:
        return self.get_name() or self.get_telethon_name()

    async def get_mention(self) -> str:
        name = self.get_display_name()
        # if config.replace_id is set then use id (as user!)
        # user -> tg://user?id=123456789
        # public channel, group -> t.me/username
        rid = self.get_redirect()
        uid = rid or self.sender.id
        username = ''
        if type(self.sender) != telethon.tl.types.User and not rid:
            # use username if applicable
            username = self.sender.username
        if username:
            return f"[{utils.str.escape(name)}](t.me/{username})"
        return f"[{utils.str.escape(name)}](tg://user?id={uid})"

    async def userpic(self) -> PIL.Image.Image | None:
        by = io.BytesIO()
        await self.client.download_profile_photo(self.sender, file=by)
        by.seek(0)
        try:
            return PIL.Image.open(by)
        except:
            return None

    def get_pronouns(self) -> list[int]:
        (pronouns,) = cur.execute("SELECT pronoun_set FROM users WHERE id = ?", (self.sender.id,)).fetchone()
        if pronouns is None:
            return None
        if pronouns == '-1': return [-1]
        assert pronouns.isdigit()
        return list(map(int, pronouns))

    def set_pronouns(self, pronoun_set: None | list[int]):
        cur.execute(
            "UPDATE users SET pronoun_set = ?, stamp = ? WHERE id = ?",
            (
                pronoun_set and ''.join(map(str, pronoun_set)),
                utils.common.stamp(),
                self.sender.id
            )
        )

    def get_name(self) -> str | None:
        return cur.execute("SELECT name FROM users WHERE id = ?", (self.sender.id,)).fetchone()[0]

    def set_name(self, name: None | str):
        cur.execute("UPDATE users SET name = ?, stamp = ? WHERE id = ?", (name, utils.common.stamp(), self.sender.id))

    def get_redirect(self) -> int | None:
        return cur.execute("SELECT replace_id FROM users WHERE id = ?", (self.sender.id,)).fetchone()[0]

    def set_redirect(self, uid: int):
        cur.execute("UPDATE users SET replace_id = ?, stamp = ? WHERE id = ?", (uid, utils.common.stamp(), self.sender.id))

    def get_lang(self) -> str:
        return cur.execute("SELECT lang FROM users WHERE id = ?", (self.sender.id,)).fetchone()[0]

    def set_lang(self, lang: str):
        cur.execute("UPDATE users SET lang = ?, stamp = ? WHERE id = ?", (lang, utils.common.stamp(), self.sender.id))


async def from_telethon(user: telethon.tl.types.User | telethon.tl.types.Channel | telethon.tl.types.Chat | str | int,
                        chat: telethon.tl.types.Chat | int | None,
                        client: telethon.client.telegramclient.TelegramClient) -> User:
    if isinstance(user, (str, int)):
        user = await client.get_entity(await client.get_input_entity(user))
    if isinstance(chat, int):
        chat = await client.get_entity(await client.get_input_entity(user))
    if not user:
        user = chat
    return User(user, chat, client)


# mention:
#  OR:
#    @(username)
#      where username is (a-zA-Z0-9_){5,64} and can't start with digit
#                        -> using simple check (word-like character)
#    {(uid)|(len)}(name)
#      where uid  is number
#            len  is number
#            name is string of len=len
mention_pattern = utils.regex.ignore_case(
    utils.regex.unite(
        '@' + utils.regex.named('username', r'\w+'),
        r'\{' + utils.regex.named_int('uid') + r'\|' + utils.regex.named_int('len') + r'\}'
    )
)


async def from_str(arg: str, chat_id: int, client: telethon.client.telegramclient.TelegramClient) -> tuple[str, User | None, str, str]:
    match = re.search(utils.user.mention_pattern, arg)
    if not match:
        return arg, None, '', ''

    m = match[0]
    idx = match.span()[0]
    pre_arg, arg = arg[:idx], arg[idx:]

    # if matched 'username' then get name
    # if matched 'uid + len' then get name from text
    vars = match.groupdict()

    if vars['username'] is not None:
        username, arg = m[1:], arg[len(m):]
        try:
            cur_user = await utils.user.from_telethon(username, chat=chat_id, client=client)
            mention = await cur_user.get_mention()
        except ValueError:
            cur_user = None
            mention = f"@{username}"
    else:
        uid = int(vars['uid'])
        l = int(vars['len'])
        arg = arg[len(m):]
        name, arg = arg[:l], arg[l:]
        cur_user = await utils.user.from_telethon(uid, chat=chat_id, client=client)
        mention = f"[{utils.str.escape(name)}](tg://user?id={uid})"

    return pre_arg, cur_user, mention, arg

