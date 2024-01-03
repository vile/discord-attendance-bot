import discord
from discord.ext import commands, tasks
from discord import app_commands
import shelve


# Helper functions
def shelve_get_instructors() -> list[int]:
    with shelve.open("database") as handle:
        return handle["instructors"] if "instructors" in handle else []


def shelve_add_instructor(user_id: discord.Member.id) -> bool:
    if user_id in shelve_get_instructors():
        return False

    with shelve.open("database") as handle:
        temp_instructors: list[int] = handle["instructors"]
        temp_instructors.append(user_id)
        handle["instructors"] = temp_instructors

    return user_id in shelve_get_instructors()


def shelve_remove_instructor(user_id: discord.Member.id) -> bool:
    if not user_id in shelve_get_instructors():
        return False

    with shelve.open("database") as handle:
        temp_instructors: list[int] = handle["instructors"]
        temp_instructors.remove(user_id)
        handle["instructors"] = temp_instructors

    return not user_id in shelve_get_instructors()


# Checks
def only_instructor_or_owner():
    def predicate(interaction: discord.Interaction) -> bool:
        return (
            interaction.user.id in shelve_get_instructors()
            or interaction.client.is_owner(interaction.user)
        )

    return app_commands.check(predicate)


class AttendanceCommandsCog(commands.GroupCog, name="attendance"):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.session_id = ""
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        print(f"[+] {self.__cog_name__} loaded")
        await self.client.tree.sync()

    @app_commands.command()
    @only_instructor_or_owner()
    async def add_instructor(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        success: bool = shelve_add_instructor(member.id)
        if not success:
            await interaction.response.send_message(
                "Sorry, I couldn't add this member as an instructor. Are they already an instructor?",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"Successfully added {member.mention} as an instructor!",
            ephemeral=True,
        )

    @app_commands.command()
    @only_instructor_or_owner()
    async def remove_instructor(
        self, interaction: discord.Interaction, member: discord.Member
    ) -> None:
        success: bool = shelve_remove_instructor(member.id)
        if not success:
            await interaction.response.send_message(
                "I couldn't remove this member. Are you sure they're an existing instructor?",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"Successfully removed  {member.mention} as an instructor!",
            ephemeral=True,
        )

    @app_commands.command()
    @only_instructor_or_owner()
    async def show_instructors(self, interaction: discord.Interaction) -> None:
        list_of_instructors: list[int] = shelve_get_instructors()
        formatted_message: str = ", ".join(f"<@{instructor}>" for instructor in list_of_instructors)  # fmt: skip
        await interaction.response.send_message(formatted_message, ephemeral=True)

    @app_commands.command()
    @only_instructor_or_owner()
    async def start_session(self, interaction: discord.Interaction) -> None:
        ...

    @app_commands.command()
    @only_instructor_or_owner()
    async def stop_session(
        self, interaction: discord.Interaction, session_id: str
    ) -> None:
        ...

    @tasks.loop(time=...)
    async def snapshot_task(self) -> None:
        ...

    @snapshot_task.before_loop
    async def before_snapshot_task(self) -> None:
        ...

    @snapshot_task.after_loop
    async def after_snapshot_task(self) -> None:
        ...

    def cog_unload(self) -> None:
        self.snapshot_task.cancel()

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: commands.CommandError
    ) -> None:
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "Sorry, you have to be an instructor to use this command.",
                ephemeral=True,
            )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(AttendanceCommandsCog(client))
