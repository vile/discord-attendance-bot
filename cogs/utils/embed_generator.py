from discord import Embed, Colour
from typing import Union


async def create_embed(
    message: str,
    title: Union[str, None] = None,
    color: Colour = Colour.green(),
) -> Embed:
    embed: Embed = Embed(
        description=message,
        title=title,
        color=color,
    )
    return embed


async def create_embed_error(
    message: str,
) -> Embed:
    embed: Embed = await create_embed(
        message,
        title="Error",
        color=Colour.red(),
    )
    return embed
