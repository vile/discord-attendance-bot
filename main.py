import asyncio
import os
import shelve

import discord
from discord.ext import commands
from dotenv import load_dotenv

import cogs.utils.constants as constants


class AttendanceBot(commands.Bot):
    def __init__(self) -> None:
        client_intents = discord.Intents.default()

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=client_intents,
            help_command=None,
        )

    async def load_extensions(self) -> None:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")

    async def setup_hook(self) -> None:
        await self.load_extensions()


async def main() -> None:
    load_dotenv()

    # Set up simple persistence
    with shelve.open(constants.SHELVE_DATABASE_NAME) as handle:
        if "instructors" not in handle:
            handle["instructors"] = []

        if "minimum_attendance_rate" not in handle:
            handle["minimum_attendance_rate"] = constants.DEFAULT_MINIMUM_ATTENDANCE_RATE_PERCENTAGE  # fmt: skip

        if "snapshot_interval" not in handle:
            handle["snapshot_interval"] = constants.DEFAULT_SNAPSHOT_INTERVAL_SECONDS  # fmt: skip

        # Always reset snapshots when bot is restarted
        handle["snapshots"] = []

        """
        instructors: list[int]
        - list of ints (user ids) that are later used to retrieve full discord.User objects

        snapshots: list[int]
        - list of ints (user ids) that were in the VC (in attendance) when the snapshot was taken
        """

    client: AttendanceBot = AttendanceBot()
    async with client:
        await client.start(os.getenv("DISCORD_BOT_TOKEN"))


if __name__ == "__main__":
    discord.utils.setup_logging()
    asyncio.run(main())
