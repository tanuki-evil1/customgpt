from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message


class TelegramBot:
    def __init__(self, token):
        self.dp = Dispatcher()
        self.token = token
        self.bot = Bot(token=self.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        @self.dp.message()
        async def echo_handler(message: Message, answer="Gang") -> None:
            """
            Handler will forward receive a message back to the sender

            By default, message handler will handle all message types (like a text, photo, sticker etc.)
            """
            try:
                # Send a copy of the received message
                await message.answer(answer)
            except TypeError:
                # But not all the types is supported to be copied so need to handle it
                await message.answer("Nice try!")

    async def start(self) -> None:
        await self.dp.start_polling(self.bot)

    async def stop(self) -> None:
        await self.bot.close()
