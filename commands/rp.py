import dataclasses
import re
import typing
import utils.cm
import utils.common
import utils.locale
import utils.log
import utils.pronouns
import utils.rand
import utils.regex
import utils.str
import utils.user


log = utils.log.get("rp")


def inflect_mention(user: utils.user.User, mention: str, form: str, lt) -> str:
    le, ri = 1, mention.rindex(']')
    inflected = lt.inflect(mention[le:ri], form, utils.pronouns.to_int(user.get_pronouns()))
    assert isinstance(inflected, str)
    return mention[:le] + inflected + mention[ri:]


def inflect_mentions(mentions: list[tuple[utils.user.User, str]], form: str, lt) -> str:
    if not mentions:
        return ""
    anded = lt.ander(inflect_mention(mention[0], mention[1], form, lt) for mention in mentions)
    assert isinstance(anded, str)
    return anded


def to_role(words: list[str], p: int) -> str:
    return ''.join(utils.locale.try_verb_past(w, p) for w in words if w)


@dataclasses.dataclass
class RP2Handler:
    emoji: str
    pattern: re.Pattern[str]
    verb: str | typing.Callable[[], str] = ''
    lang: str = "ru"
    form: str = "accs"
    compiled_pattern = None

    def __post_init__(self):
        self.lang = utils.locale.lang(self.lang)
        self.compiled_pattern = utils.regex.cmd(self.pattern)

    def invoke(self, user: str, pronouns: None | int | list[int], mentions: list[tuple[utils.user.User, str]], comment: str) -> str:
        verb = (self.verb or self.pattern) if type(self.verb) == str else self.verb()
        verb = utils.regex.split_by_word_border(verb)
        return "{e} | {s} {v} {m} {c}".format(
            e=self.emoji,
            s=user,
            v=to_role(verb, utils.pronouns.to_int(pronouns)),
            m=inflect_mentions(mentions, self.form, self.lang),
            c=comment,
        ).strip().replace('  ', ' ', 1)


rp2handlers = [
    RP2Handler("🤗", "обнять"),
    RP2Handler("😈", "выебать"),
    RP2Handler("🔧", "сломать"),
    RP2Handler("☠", "убить"),
    RP2Handler("🔫", "расстрелять"),
    RP2Handler("😘", "поцеловать"),
    RP2Handler("👞", "пнуть"),
    RP2Handler("🤲", "прижать"),
    RP2Handler("🤲", "погладить"),
    RP2Handler("🙌", "потрогать"),
    RP2Handler("👅", "лизнуть"),
    RP2Handler("👃", "понюхать"),
    RP2Handler("🤜😵", "ударить"),
    RP2Handler("👏", "шлепнуть"),
    RP2Handler("👏", "шлёпнуть"),
    RP2Handler("😬", "кусь(нуть){0,1}|укусить", verb="кусьнуть"),
    RP2Handler("🎁", "дать", form="datv"),
    RP2Handler("🍻", "предложить пива", form="datv"),
    RP2Handler("🪟", "дефенестрировать", utils.rand.rand_or_null_fun("отправить в свободное падение", 1, 2, "измучить виндой")),
]
rp2handlers_regex = utils.regex.cmd(utils.regex.union(h.pattern for h in rp2handlers))


async def on_rp(cm: utils.cm.CommandMessage) -> None:
    user = await cm.sender.get_mention()
    pronoun_set = cm.sender.get_pronouns()
    default_mention = [(cm.reply_sender, await cm.reply_sender.get_mention())] if cm.reply_sender is not None else []
    chat = cm.sender.chat
    client = cm.client
    res = []
    for line in cm.arg.split('\n')[:20]:  # technical limitation TODO fix!
        cur_pronoun_set = utils.pronouns.to_int(pronoun_set)
        # try match to RP-2 as "RP-2 [mention] arg"
        for handler in rp2handlers:
            try:
                match = re.search(handler.compiled_pattern, line)
                if match:
                    arg = line[len(match[0]):]
                    arg = arg.lstrip()
                    match = re.search(utils.user.mention_pattern, arg)
                    cur_mention = []
                    while match:
                        # if matched 'username' then get name
                        # if matched 'uid + len' then get name from text TODO
                        vars = match.groupdict()
                        if vars['username'] is not None:
                            username, arg = match[0][1:], arg[len(match[0]):]
                            cur_user = await utils.user.from_telethon(username, chat, client)
                            mention = await cur_user.get_mention()
                        else:
                            uid = int(vars['uid'])
                            l = int(vars['len'])
                            arg = arg[len(match[0]):]
                            name, arg = arg[:l], arg[l:]
                            cur_user = await utils.user.from_telethon(uid, chat, client)
                            mention = f"[{utils.str.escape(name)}](tg://user?id={uid})"
                        cur_mention.append((cur_user, mention))
                        arg = arg.lstrip()
                        match = re.search(utils.user.mention_pattern, arg)
                    cur_mention = cur_mention or default_mention

                    if cur_mention or arg:
                        res.append(handler.invoke(user, cur_pronoun_set, cur_mention, arg))
            except ValueError:
                res.append("Could not parse mention")
    if res:
        await cm.int_cur.reply('\n'.join(res), link_preview=False)


async def on_role(cm: utils.cm.CommandMessage) -> None:
    self_mention = [(cm.sender, await cm.sender.get_mention())]
    pronoun_set = cm.sender.get_pronouns()
    default_mention = [(cm.reply_sender, await cm.reply_sender.get_mention())] if cm.reply_sender is not None else []
    chat = cm.sender.chat
    client = cm.client
    res = []
    for line in cm.arg.split('\n'):
        if not line or len(line) < 2 or line[0] != '~' or line[-1] == '~' or line[1].isdigit():
            continue

        line = f"MENTION0 {line[1:]}"
        mentions = self_mention[:]

        pre, user, mention, post = await utils.user.from_str(line, chat, client)
        while user:
            line = f"{pre}MENTION{len(mentions)}{post}"
            mentions.append((user, mention))
            pre, user, mention, post = await utils.user.from_str(line, chat, client)

        words = utils.regex.split_by_word_border(line)
        line = to_role(words, utils.pronouns.to_int(pronoun_set))  # TODO inflect mentions!!
        need_second_mention = len(words) <= 5

        if '%' in line and default_mention:
            line = line.replace('%', f'MENTION{len(mentions)}')
            mentions.extend(default_mention)

        if need_second_mention and len(mentions) == 1:
            mentions.extend(default_mention)
            line = f"{line} MENTION1"

        if not need_second_mention or len(mentions) != 1:
            for i in range(len(mentions) - 1, -1, -1):
                line = line.replace(f'MENTION{i}', mentions[i][1])
            res.append(line)
    if res:
        await cm.int_cur.reply('\n'.join(res), link_preview=False)


handler_list = [
    utils.cm.CommandHandler("role", rp2handlers_regex, "rp2", on_rp),
    utils.cm.CommandHandler("role-new", utils.regex.ignore_case("(^|\n)~.*(?<!~)($|\n)"), "rp3", on_role),
]

