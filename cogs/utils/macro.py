from typing import Literal

import discord
from discord import Embed

from cogs.enums.embed_type import EmbedType
from cogs.utils.embed_generator import create_embed, create_embed_error


async def send_embed(
    interaction: discord.Interaction,
    embed_type: Literal[EmbedType.NORMAL, EmbedType.ERROR] = EmbedType.NORMAL,
    is_ephemeral: bool = True,
    **embed_kwargs,
) -> None:
    """Macro to send an interaction response with an embed"""
    match embed_type:
        case EmbedType.NORMAL:
            embed: Embed = await create_embed(**embed_kwargs)
        case EmbedType.ERROR:
            embed: Embed = await create_embed_error(**embed_kwargs)
        case _:
            embed: Embed = Embed()

    await interaction.response.send_message(embed=embed, ephemeral=is_ephemeral)
