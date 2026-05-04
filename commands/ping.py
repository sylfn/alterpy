import datetime
import typing
import utils.cm
import utils.common
import utils.lang.ru
import utils.locale
import utils.regex
import utils.system
import utils.time
import utils.user
import zoneinfo


handler_list: list[utils.cm.CommandHandler] = []

start_time = datetime.datetime.now(datetime.timezone.utc)

tzMSK = zoneinfo.ZoneInfo("Europe/Moscow")

time_format = "(%Z) %Y-%m-%d, %H:%M:%S"

translations = {
    'ping_message': {
        'en': '**{rep}**. Ping is {ping}, handled in {handle}\nUp for {up}',
        'ru': '**{rep}**. Пинг — {ping}, обработка — {handle}\nНе падает, работает {up}!',
    },
    'ping_reply': {
        'en': 'PONG',
        'ru': 'ПОНГ',
    },
    'test_reply': {
        'en': 'PASSED',
        'ru': 'ПРОЙДЕН',
    },
    'stat_message': {
        'en': '''——— AlterPy ———
Running on `{system_info}`
Ping is _{ping}_, handled in _{handle}_
Up for _{up}_
This chat ID is `{cm.sender.chat.id}`
{user_count} known users from {chat_count} known chats

— Current time is —
`{cur_time.astimezone(tzMSK).strftime(time_format)}`
— Started at —
`{start_time.astimezone(tzMSK).strftime(time_format)}`''',
        'ru': '''——— АльтерПай ———
Запущена на `{system_info}`
Пинг — _{ping}_, обработка — _{handle}_
Не падает, работает _{up}_
ID чата — `{cm.sender.chat.id}`
{user_count} пользователей из {chat_count} чатов

— Текущее время —
`{cur_time.astimezone(tzMSK).strftime(time_format)}`
— Время запуска —
`{start_time.astimezone(tzMSK).strftime(time_format)}`'''
    }
}
LOC = utils.locale.Localizator(translations)


def get_ping_times(cm: utils.cm.CommandMessage) -> tuple[str, str, str]:
    """return ping, handle and up formatted times"""
    cur_time = datetime.datetime.now(datetime.timezone.utc)

    ping = cm.local_time - cm.time
    handle = cur_time - cm.local_time
    up = cur_time - start_time

    ping_s = utils.time.timedelta_to_str(ping, is_short=True, lang=cm.lang)
    handle_s = utils.time.timedelta_to_str(handle, is_short=True, lang=cm.lang)
    up_s = utils.time.timedelta_to_str(up, lang=cm.lang, form={"accs"})
    return ping_s, handle_s, up_s


async def on_ping(cm: utils.cm.CommandMessage) -> None:
    ping, handle, up = get_ping_times(cm)
    rep = eval(LOC.get('ping_reply', cm.lang))
    msg = eval(LOC.get('ping_message', cm.lang))
    await cm.int_cur.reply(msg)


async def on_test(cm: utils.cm.CommandMessage) -> None:
    ping, handle, up = get_ping_times(cm)
    rep = eval(LOC.get('test_reply', cm.lang))
    msg = eval(LOC.get('ping_message', cm.lang))
    await cm.int_cur.reply(msg)


async def on_stat(cm: utils.cm.CommandMessage) -> None:
    cur_time = datetime.datetime.now(datetime.timezone.utc)
    ping, handle, up = get_ping_times(cm)
    system_info = utils.system.system_info()
    user_count = utils.user.user_count()
    chat_count = utils.user.chat_count()
    msg = eval(LOC.get('stat_message', cm.lang))
    await cm.int_cur.reply(msg)


def replier(ans: str) -> typing.Callable[[utils.cm.CommandMessage], typing.Awaitable[None]]:
    async def on_reply(cm: utils.cm.CommandMessage) -> None:
        await cm.int_cur.reply(ans)
    return on_reply


handler_list.append(utils.cm.CommandHandler(name="ping", pattern=utils.regex.cmd("(ping|пинг)$"), help_page="ping", handler_impl=on_ping))
handler_list.append(utils.cm.CommandHandler(name="test", pattern=utils.regex.cmd("(test|тест)$"), help_page="test", handler_impl=on_test))
handler_list.append(utils.cm.CommandHandler(name="stat", pattern=utils.regex.cmd("(stat|стат|инфо)$"), help_page="ping", handler_impl=on_stat))

handler_list.extend(
    utils.cm.CommandHandler(
        name=msg,
        pattern=utils.regex.ignore_case(utils.regex.pat_starts_with(pat)),
        help_page="ping",
        handler_impl=replier(ans)
    ) for msg, ans, pat in [
        ("bot", "I'm here!", "bot$"),
        ("бот", "На месте!", "бот$"),
        ("ты где", "Я тут", "(ты где)|(где ты)$"),
        ("сдох", "Ты тоже.", "сдох\\?$"),
        ("слава партии", "Слава Партии!", "слава партии[\\?!]*"),
        ("кто здесь власть", "ПАРТИЯ!", "кто здесь власть[\\?]*"),
    ]
)
