import asyncio
import os
import shelve

import discord
from discord.ext import commands
from dotenv import load_dotenv


class AttendanceBot(commands.Bot):
    def __init__(self) -> None:
        client_intents = discord.Intents.all()
        client_intents.presences = False
        client_intents.members = False
        client_intents.message_content = False

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=client_intents,
        )

        self.remove_command("help")

    async def setup_hook(self) -> None:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")

        await self.tree.sync()


async def main() -> None:
    load_dotenv()

    # Set up simple persistence
    with shelve.open("database") as handle:
        if "instructors" not in handle:
            handle["instructors"] = []

        if "minimum_attendance_rate" not in handle:
            handle["minimum_attendance_rate"] = 0.5  # percentage

        if "snapshot_interval" not in handle:
            handle["snapshot_interval"] = 3  # seconds

        # Always reset snapshots when bot is restarted
        handle["snapshots"] = []

        """
        instructors: list[int]
        - list of ints (user ids) that are later used to retrieve full discord.User objects

        snapshots: list[int]
        - list of ints (user ids) that were in the VC (in attendance) when the snapshot was taken
        """

    client = AttendanceBot()
    async with client:
        await client.start(os.getenv("DISCORD_BOT_TOKEN"))


if __name__ == "__main__":
    discord.utils.setup_logging()
    asyncio.run(main())
