import discord
from discord.ext import commands
import os


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

        # Load cogs
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                self.load_extension(f"cogs.{filename[:-3]}")

    def run(self) -> None:
        super().run()


def main() -> None:
    client = AttendanceBot()
    client.run()


if __name__ == "__main__":
    main()
