import logging
from typing import Literal, Optional

import discord
from discord.ext import commands


@commands.is_owner()
@commands.guild_only()
class SyncComanndsCog(
    commands.GroupCog,
    name="dev",
):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.logger = logging.getLogger(f"cogs.{self.__cog_name__}")

    @commands.command()
    async def sync(
        self,
        ctx: commands.Context,
        guilds: commands.Greedy[discord.Object],
        spec: Optional[Literal["~", "*", "^"]] = None,
    ) -> None:
        can_send_messages: bool = ctx.channel.permissions_for(
            ctx.guild.get_member(self.client.application_id)
        ).send_messages

        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            message: str = (
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            self.logger.info(message)
            if can_send_messages:
                await ctx.send(message)
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        message: str = f"Synced the tree to {ret}/{len(guilds)}."
        self.logger.info(message)
        if can_send_messages:
            await ctx.send(message)

    @commands.command()
    async def reload(self, ctx: commands.Context, cog: str) -> None:
        can_send_messages: bool = ctx.channel.permissions_for(
            ctx.guild.get_member(self.client.application_id)
        ).send_messages

        try:
            await self.client.reload_extension(f"cogs.{cog}")
        except Exception as error:
            self.logger.info(f"Failed to reload cogs.{cog}, {error}")
            if can_send_messages:
                await ctx.send(
                    f"Failed to reload the `{cog}` cog. Does this cog/extension exist?"
                )
                return

        self.logger.info(f"Successfully reloaded cogs.{cog}")
        if can_send_messages:
            await ctx.send(f"Successfully reloaded the `{cog}` cog")


async def setup(client: commands.Bot) -> None:
    cog: SyncComanndsCog = SyncComanndsCog(client)
    await client.add_cog(cog)
    cog.logger.info("Cog loaded")
