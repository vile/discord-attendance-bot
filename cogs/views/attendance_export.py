from io import StringIO
from time import time
from typing import Any
from uuid import uuid4

import discord
import requests
from discord import ButtonStyle, Embed, app_commands
from discord.ext import commands
from discord.ui.item import Item
from requests import Response

import cogs.utils.constants as constants
import cogs.utils.interaction_checks as interaction_checks
from cogs.utils.embed_generator import create_embed, create_embed_error


class AttendanceExportButtons(discord.ui.View):
    def __init__(
        self,
        client: commands.Bot,
        attendance_data: dict,
        timeout: int = constants.BUTTON_VIEW_TIMEOUT,
    ) -> None:
        self.client = client
        self.attendance_data = attendance_data
        self.message = None
        super().__init__(timeout=timeout)

    async def attendance_data_to_csv(self) -> str:
        csv_str: str = f"{constants.CSV_HEADERS}\n"

        for member, did_attend in self.attendance_data.items():
            csv_str += f"{member},{did_attend}\n"

        return csv_str

    @discord.ui.button(label="Generate CSV", style=discord.ButtonStyle.blurple)
    async def generate_csv_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        button.disabled = True
        await interaction.message.edit(view=self)

        csv: str = await self.attendance_data_to_csv()
        timestamp: int = int(time())
        filename: str = f"attendance_export_{timestamp}.csv"
        string_io_file: StringIO = StringIO(csv)

        await interaction.response.send_message(
            file=discord.File(string_io_file, filename=filename),
        )

    @discord.ui.button(
        label="Upload to Mystbin (CSV)", style=discord.ButtonStyle.blurple
    )
    async def generate_mystbin_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        button.disabled = True
        await interaction.message.edit(view=self)

        csv: str = await self.attendance_data_to_csv()
        timestamp: int = int(time())
        filename: str = f"attendance_export_{timestamp}.csv"
        password: str = uuid4().hex[:12]  # Create sudo-random password for paste

        json: dict = {
            "password": password,
            "files": [{"content": csv, "filename": filename}],
        }
        response: Response = requests.put(constants.MYSTBIN_PASTE_API, json=json)
        if response.status_code != 201:
            embed: Embed = await create_embed_error(
                "Sorry, there seemed to have been an issue uploading this file to Mystbin"
            )
            await interaction.response.send_message(embed=embed)
            return

        paste_id: str = response.json()["id"]
        embed: Embed = await create_embed(
            f"Your CSV has been uploaded with the password ||`{password}`||\n\nhttps://mystb.in/{paste_id}"
        )
        await interaction.response.send_message(embed=embed)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if await interaction_checks.user_is_instructor_or_owner(
            self.client, interaction
        ):
            return True
        raise app_commands.CheckFailure()

    async def on_error(
        self, interaction: discord.Interaction, error: Exception, item: Item[Any]
    ) -> None:
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "Sorry, you have to be an instructor to use this command.",
                ephemeral=True,
            )

    async def on_timeout(self) -> None:
        for child in self.children:
            child.style = ButtonStyle.gray
            child.disabled = True
        await self.message.edit(view=self)
