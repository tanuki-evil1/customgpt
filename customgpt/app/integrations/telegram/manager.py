import asyncio


class TelegramBotManager:
    def __init__(self) -> None:
        self.bots = []

    async def start_all_bots(self):
        tasks = [asyncio.create_task(bot.start()) for bot in self.bots]
        await asyncio.gather(*tasks)

    async def stop_all_bots(self):
        for bot in self.bots:
            self.bots.remove(bot)
            await bot.stop()
