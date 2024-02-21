import logging
import os

import discord
from discord import Activity, ActivityType, app_commands
from discord.ext import commands, tasks

import cogs.utils.constants as constants
import cogs.utils.shelve_utils as shelve_utils


@app_commands.guild_only()
class PresenceCommandsCog(
    commands.GroupCog,
    name="presence",
):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.logger = logging.getLogger(f"cogs.{self.__cog_name__}")

    @tasks.loop(seconds=constants.PRESENCE_TASK_LOOP_SECONDS)
    async def presence_task(self) -> None:
        snapshots: list[int] = shelve_utils.get_snapshots()

        attendance_total: dict = {}
        for snapshot in snapshots:
            for member in snapshot:
                if member in attendance_total:
                    attendance_total[member] += 1
                else:
                    attendance_total[member] = 1

        num_students: int = len(attendance_total.keys())
        activity_name: str = f"{num_students} student{'s' if num_students != 1 else ''}"
        activity_game: Activity = Activity(
            name=activity_name, type=ActivityType.watching
        )
        await self.client.change_presence(activity=activity_game)

    @presence_task.after_loop
    async def presence_task_after_loop(self) -> None:
        self.logger.info("Task stopped, removing presence")
        await self.client.change_presence()

    def cog_unload(self) -> None:
        self.presence_task.cancel()


async def setup(client: commands.Bot) -> None:
    cog: PresenceCommandsCog = PresenceCommandsCog(client)
    await client.add_cog(cog, guild=discord.Object(int(os.getenv("GUILD_ID"))))
    cog.logger.info("Cog loaded")
