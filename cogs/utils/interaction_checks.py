from discord import Interaction
from discord.ext import commands

import cogs.utils.shelve_utils as shelve_utils


async def user_is_instructor(interaction: Interaction) -> bool:
    if interaction.user.id in shelve_utils.get_instructors():
        return True
    return False


async def user_is_owner(client: commands.Bot, interaction: Interaction) -> bool:
    return await client.is_owner(interaction.user)


async def user_is_instructor_or_owner(
    client: commands.Bot, interaction: Interaction
) -> bool:
    if await user_is_instructor(interaction):
        return True
    if await user_is_owner(client, interaction):
        return True
    return False
