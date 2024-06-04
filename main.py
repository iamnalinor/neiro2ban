import asyncio
import datetime
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ChatType, UpdateType
from aiogram.exceptions import TelegramAPIError
from envparse import env

env.read_envfile(".env")

logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

dp = Dispatcher()

MessageIdPair = "tuple[int, int]"
message_dates: "dict[MessageIdPair, datetime.datetime]" = {}

REACTION_SECONDS_THRESHOLD = 10
BIO_KEYWORD = "@creaitors_bot"


@dp.startup()
async def on_startup(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)


@dp.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def handle_start_command(message: types.Message):
    await message.answer(r"¯\_(ツ)_/¯")


@dp.message(F.chat.type == ChatType.SUPERGROUP)
async def handle_message(message: types.Message):
    message_dates[(message.chat.id, message.message_id)] = message.date

    for key, value in message_dates.copy().items():
        # using message.date instead of datetime.datetime.now()
        if (message.date - value).total_seconds() > REACTION_SECONDS_THRESHOLD:
            del message_dates[key]


@dp.message_reaction(F.user & (F.old_reaction.len() == 0) & (F.new_reaction.len() == 1))
async def handle_message_reaction(update: types.MessageReactionUpdated, bot: Bot):
    message_params = f"chat_id={update.chat.id} message_id={update.message_id}"

    logger.info(
        f"Reaction {update.new_reaction[0].emoji} added to message {message_params}"
    )

    message_id = update.message_id
    message_date = message_dates.get((update.chat.id, message_id))
    if message_date is None:
        logger.warning(
            f"Message date not found for {message_params} (probably it was sent too long ago), skipping"
        )
        return

    duration = update.date - message_date
    if duration.total_seconds() > REACTION_SECONDS_THRESHOLD:
        logger.warning(f"Message sent {duration} ago (>{REACTION_SECONDS_THRESHOLD} seconds), skipping")
        return

    user_bio = (await bot.get_chat(update.user.id)).bio
    if user_bio is None:
        logger.warning(f"User {update.user.id} has no bio, skipping")
        return

    if BIO_KEYWORD.casefold() not in user_bio.casefold():
        logger.warning(f"User {update.user.id} has no target keyword in bio={user_bio}, skipping")
        return

    logger.warning(
        f"User {update.user.id} {update.user.first_name} seems to be a bot with bio={user_bio}, banning"
    )
    try:
        await bot.ban_chat_member(update.chat.id, update.user.id)
    except TelegramAPIError:
        logger.exception(f"Failed to ban user {update.user.id} in chat {update.chat.id}")


async def main():
    bot = Bot(token=env.str("BOT_TOKEN"))
    await dp.start_polling(bot, allowed_updates=[UpdateType.MESSAGE, UpdateType.MESSAGE_REACTION])


if __name__ == "__main__":
    asyncio.run(main())
