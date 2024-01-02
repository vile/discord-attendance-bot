import discord
from discord.ext import commands
from discord import app_commands


# Checks
def instructor_only():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == ...

    return app_commands.check(predicate)


class AttendanceCommands(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
