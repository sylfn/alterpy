import utils.command
import utils.pronouns
import utils.regex
import utils.str
import utils.locale
import utils.user

handler_list = []

translations = {
    'set_name_empty': {
        'en': 'Can not set name to empty one. To reset name use `-name`',
        'ru': 'Невозможно установить пустое имя. Для сброса используйте `-имя`',
    },
    'set_name': {
        'en': 'Name set to {name}',
        'ru': 'Установлено имя {name}',
    },
    'reset_name': {
        'en': 'Name is now unset',
        'ru': 'Имя сброшено',
    },
    'set_pronouns_empty': {
        'en': 'To set pronouns to empty, use `+pn void`. To reset pronouns, use `-pn`',
        'ru': 'Чтобы использовать пустые местоимения, используйте `+мест нет`. Чтобы сбросить местоимения, используйте `-мест`',
    },
    'set_pronouns': {
        'en': 'Pronouns set to {pns}',
        'ru': 'Установлены местоимения {pns}',
    },
    'reset_pronouns': {
        'en': 'Pronouns are now unset',
        'ru': 'Местоимения сброшены',
    },
    'set_redirect_empty': {
        'en': 'Can not set mention redirect to empty. To reset use `-redir`',
        'ru': 'Невозможно установить пустое перенаправление. Для сброса используйте `-напр`',
    },
    'set_redirect': {  # TODO
        'en': 'Mention redirect set to {rid}',
        'ru': 'Перенаправление упоминаний установлено на {rid}',
    },
    'reset_redirect': { 
        'en': 'Redirect set to nothing',
        'ru': 'Перенаправление упоминаний сброшено',
    },
    'set_lang_empty': {
        'en': 'Can not set lang to empty. To reset use `-lang`',
        'ru': 'Невозможно установить пустой язык. Для сброса используйте `-язык`',
    },
    'set_lang': {
        'en': 'Language set to {lang}',
        'ru': 'Установлен язык {lang}',
    },
    'reset_lang': {
        'en': 'Language is reset',
        'ru': 'Язык сброшен',
    },
    'get': {  # TODO
        'en': "{name}'s pronouns are {pns}. Name set? {has_name}. Redirect? {rid}",
        'ru': "Набор местоимений {name} — {pns}. Установлено имя? {has_name}. Перенаправление? {rid}",
    }
}

LOC = utils.locale.Localizator(translations)


async def on_set_name(cm: utils.command.Message) -> None:
    if not cm.arg:
        await cm.int_cur.reply(LOC.obj('set_name_empty', cm.lang))
        return
    name = cm.arg
    cm.sender.set_name(name)
    name = utils.str.escape(name)
    await cm.int_cur.reply(eval(LOC.get('set_name', cm.lang)))


async def on_reset_name(cm: utils.command.Message) -> None:
    cm.sender.set_name(None)
    await cm.int_cur.reply(LOC.obj('reset_name', cm.lang))


async def on_set_pronouns(cm:utils.command.Message) -> None:
    if not cm.arg:
        await cm.int_cur.reply(LOC.obj('set_pronouns_empty', cm.lang))
        return
    pns_s = cm.arg
    pns_i = utils.pronouns.from_str(pns_s)
    pns = utils.pronouns.to_str(pns_i, cm.lang)
    cm.sender.set_pronouns(pns_i)
    await cm.int_cur.reply(eval(LOC.get('set_pronouns', cm.lang)))



async def on_reset_pronouns(cm: utils.command.Message) -> None:
    cm.sender.set_pronouns(None)
    await cm.int_cur.reply(LOC.obj('reset_pronouns', cm.lang))


async def on_set_redirect(cm: utils.command.Message) -> None:
    _, mentioned, _, _ = await utils.user.from_str(cm.arg, cm.sender.chat, cm.client)
    user = mentioned or cm.reply_sender
    if not user:
        await cm.int_cur.reply(LOC.obj('set_redirect_empty', cm.lang))
        return
    rid = user.sender.id
    cm.sender.set_redirect(rid)
    await cm.int_cur.reply(eval(LOC.get('set_redirect', cm.lang)))


async def on_reset_redirect(cm: utils.command.Message) -> None:
    cm.sender.set_redirect(None)
    await cm.int_cur.reply(LOC.obj('reset_redirect', cm.lang))


async def on_set_lang(cm: utils.command.Message) -> None:
    if not cm.arg:
        await cm.int_cur.reply(LOC.obj('set_lang_empty', cm.lang))
        return
    # TODO check if supported, maybe add lang preference list (likely to be slow but this is python, nothing new)
    lang = cm.arg
    cm.sender.set_lang(lang)
    await cm.int_cur.reply(eval(LOC.get('set_lang', cm.lang)))


async def on_reset_lang(cm: utils.command.Message) -> None:
    cm.sender.set_lang(None)
    await cm.int_cur.reply(LOC.obj('reset_lang', cm.lang))


async def on_get(cm: utils.command.Message) -> None:
    _, mentioned, _, _ = await utils.user.from_str(cm.arg, cm.sender.chat, cm.client)
    user = mentioned or cm.reply_sender or cm.sender
    name = utils.str.escape(user.get_display_name())
    has_name = bool(user.get_name())
    pns = utils.pronouns.to_str(user.get_pronouns(), cm.lang)
    rid = user.get_redirect() or 'NOT SET'
    await cm.int_cur.reply(eval(LOC.get('get', cm.lang)))


for add, sub, get, cmd, hlp, cmds in [
    (on_set_name,     on_reset_name,     on_get, 'name',  'pronouns', ['name',  'имя']),
    (on_set_pronouns, on_reset_pronouns, on_get, 'pn',    'pronouns', ['pn',    'мест']),
    (on_set_redirect, on_reset_redirect, on_get, 'redir', 'redirect', ['redir', 'напр']),
    (on_set_lang,     on_reset_lang,     on_get, 'lang',  'lang',     ['lang',  'язык']),
]:
    rcmds = utils.regex.union(cmds)
    handler_list.extend([
        utils.command.Handler(f'+{cmd}', utils.regex.add(rcmds), hlp, add, is_prefix=True, is_arg_current=True),
        utils.command.Handler(f'-{cmd}', utils.regex.sub(rcmds), hlp, sub),
        utils.command.Handler(f'?{cmd}', utils.regex.ask(rcmds), hlp, get),
    ])

