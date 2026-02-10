import utils.ch
import utils.cm
import utils.regex


async def on_start(cm: utils.cm.CommandMessage) -> None:
    await cm.int_cur.reply(
        "Привет! На связи alterpy - полузаброшенный, но всё так же быстрый, потому что никому не нужный телеграм-бот, разработанный для t.me/theyukichat!\n" +
        "\n" +
        '"Как catpy и forkpy, только по-другому"\n' +
        "Список команд _уже не поддерживается_. Пинг до бота: `/ping`\n" +
        "\n" +
        "[Исходный код](https://github.com/sylfn/alterpy) доступен под лицензией MIT."
    )

handler_list = [utils.ch.CommandHandler(
    name="start",
    pattern=utils.regex.raw("/start(@alterpy_bot)?"),
    help_page="start",
    handler_impl=on_start,
)]

