import discord
from discord import app_commands
from discord.ext import commands, tasks

import cogs.utils.interaction_checks as interaction_checks
import cogs.utils.shelve_utils as shelve_utils


@app_commands.guild_only()
class SettingCommandsCog(
    commands.GroupCog,
    name="settings",
):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"{self.__cog_name__} cog loaded")
        await self.client.tree.sync()

    @app_commands.command(name="get-attendance", description="Get the current minimum attendance rate")  # fmt: skip
    async def get_minium_attendance(self, interaction: discord.Interaction) -> None:
        attendance_rate: float = shelve_utils.get_attendance_rate()

        await interaction.response.send_message(
            f"The current minimum attendance rate is {attendance_rate * 100:.0f}%",
            ephemeral=True,
        )

    @app_commands.command(name="set-attendance", description="Set the minimum attendance rate")  # fmt: skip
    @app_commands.describe(rate="The minimum number, in percentage (0.1 = 10%), of snapshots a user needs to be present in to be counted as in attendance")  # fmt: skip
    async def set_minimum_attendance(
        self,
        interaction: discord.Interaction,
        rate: app_commands.Range[float, 0.0, 1.0],
    ) -> None:
        success: bool = shelve_utils.set_attendace_rate(rate)

        if not success:
            await interaction.response.send_message(
                "There seems to have been an issue setting the attendance rate. Try again",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"Successfully set the required attendance rate to {rate * 100:.0f}%",
            ephemeral=True,
        )

    @app_commands.command(name="get-interval", description="Get the current snapshot interval")  # fmt: skip
    async def get_snapshot_interval(self, interaction: discord.Interaction) -> None:
        snapshot_interval: int = shelve_utils.get_snapshot_interval()

        await interaction.response.send_message(
            f"The current snapshot rate is {snapshot_interval} seconds",
            ephemeral=True,
        )

    @app_commands.command(name="set-interval", description="Set the snapshot interval")  # fmt: skip
    @app_commands.describe(interval="The time interval, in seconds, a snapshot should be taken of the members lists in the session VC")  # fmt: skip
    async def set_snapshot_interval(
        self,
        interaction: discord.Interaction,
        interval: app_commands.Range[int, 3, 900],
    ) -> None:
        attendance_cog: commands.GroupCog = self.client.get_cog("attendance")
        snapshot_task: tasks.Loop = attendance_cog.snapshot_task

        if snapshot_task.is_running() or snapshot_task.is_being_cancelled():
            await interaction.response.send_message(
                "You can't set the snapshot interval while a session is running or being canceled. Stop your current session or wait a few seconds for the current session to finish canceling",
                ephemeral=True,
            )
            return

        success: bool = shelve_utils.set_snapshot_interval(interval)

        if not success:
            await interaction.response.send_message(
                "There seems to have been an issue setting the snapshot interval. Try again",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"Successfully set the snapshot interval to {interval} seconds",
            ephemeral=True,
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if await interaction_checks.user_is_instructor_or_owner(
            self.client, interaction
        ):
            return True
        return False

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: commands.CommandError
    ) -> None:
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "Sorry, you have to be an instructor to use this command.",
                ephemeral=True,
            )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(SettingCommandsCog(client))
