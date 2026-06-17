import os
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

import discord
from discord.ext import commands


load_dotenv()

TOKEN = os.getenv("TOKEN")

BOT_NAME = "backendbot"


INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.guilds = True
INTENTS.members = True
INTENTS.messages = True


class LogFormatter(logging.Formatter):

    def format(self, record):

        timestamp = self.formatTime(
            record,
            "%H:%M:%S-%d-%m-%y"
        )

        return (
            f"[{BOT_NAME}] "
            f"{timestamp} || "
            f"({record.levelname}) "
            f"{record.getMessage()}"
        )


logger = logging.getLogger(BOT_NAME)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(LogFormatter())
logger.addHandler(handler)


class BackendBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=INTENTS,
            help_command=None
        )

        self.synced = False


    async def load_all_cogs(self):

        root = Path("./cogs")

        loaded = 0

        for folder in root.iterdir():

            if not folder.is_dir():
                continue

            if folder.name == "databases":
                continue

            if not (folder / "__init__.py").exists():
                continue

            ext = f"cogs.{folder.name}"

            try:
                await self.load_extension(ext)
                loaded += 1
                logger.info(f"Loaded {ext}")

            except Exception as e:
                logger.error(f"{ext} :: {e}")

        logger.info(f"{loaded} cog(s)")


    async def reload_all(self):

        for ext in list(self.extensions):

            try:
                await self.reload_extension(ext)
                logger.info(f"Reloaded {ext}")

            except Exception as e:
                logger.error(f"{ext} :: {e}")


    async def update_presence(self):

        await self.wait_until_ready()

        while True:

            try:

                guilds = len(self.guilds)

                members = sum(
                    g.member_count or 0
                    for g in self.guilds
                )

                for status in (
                    f"{guilds} servers",
                    f"{members} members"
                ):

                    await self.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching,
                            name=status
                        )
                    )

                    await asyncio.sleep(30)

            except Exception:
                await asyncio.sleep(10)


    async def setup_hook(self):

        await self.load_all_cogs()

        if not self.synced:

            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} commands")

            self.synced = True

        self.loop.create_task(self.update_presence())


    async def on_ready(self):

        logger.info(f"Online :: {self.user}")


bot = BackendBot()


@bot.command()
@commands.is_owner()
async def reload(ctx):

    await bot.reload_all()
    await ctx.send("Reloaded.")


def main():

    if not TOKEN:
        raise RuntimeError("TOKEN missing")

    bot.run(TOKEN)


if __name__ == "__main__":
    main()
