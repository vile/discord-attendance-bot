# Discord Attendance Bot

[![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fvile%2Fdiscord-attendance-bot%2Fmaster%2Fpyproject.toml)](https://www.python.org/)
[![Discord.py Package Version](https://img.shields.io/badge/discord.py-2.3.2-green)](https://github.com/Rapptz/discord.py)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)

A simple Discord bot for taking and reporting attendance of users within a specific voice channel.

Originally created for [Boring Security DAO](https://twitter.com/BoringSecDAO).

## Requirements

1. Git - [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
   1. Check if you have Git installed with `git --version`
2. Python (>=3.10) - [Install Python (Windows)](https://www.python.org/downloads/windows/), [Install Python (Linux)](https://docs.python.org/3/using/unix.html)
   1. Check if you have Python installed with `python3 --version`
3. Pip - [Install Pip](https://pip.pypa.io/en/stable/installation/)
   1. Check if you have Pip installed with `pip --version`

## Usage

### Creating a Discord Bot (App)

#### Creating an application

This repo assumes you understand how to create an application through the [Discord Dev Portal](https://discord.com/developers/applications) and attach a bot to it.
**It is recommended to set the bot to private** (public bot: off), as the bot is designed to be self-hosted and only interact with a single guild (server).

<details>
<summary>Disable Public Bot</summary>
<br>

![Disable your bot's Public Bot flag in the Discord Dev Portal](./images/1-disable-public-bot.jpg)

</details>

#### Invite the bot

The bot requires no intents or specific permissions when inviting it; `Send Messages` is only temporarily required during bot setup.
If the voice channel(s) you intend to use with the bot require a specific role or are otherwise restricted in some way, you need to grant an explicit `View Channel` permission to the bot for that voice channel.
Otherwise, the bot is able to view all voice channels the `@everyone` role can view.
To generate a bot invite link, go to your bot's application page in the [Discord Dev Portal](https://discord.com/developers/applications), then navigate to `OAuth2` -> `URL Generator`.
Select the `bot` and `applications.commands` scopes; no permissions are **required** (see suggested permissions below).

<details>
<summary>Required Scopes</summary>
<br>

![Discord bot invite link](./images/2-required-scopes.jpg)

</details>

<details>
<summary>Suggested Permissions</summary>
<br>

![Discord bot invite link](./images/3-suggested-permissions.jpg)

</details>

<details>
<summary>Invite Link Example</summary>
<br>

![Discord bot invite link](./images/4-bot-invite-link.jpg)

- `https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=3072&scope=bot+applications.commands`

</details>

### Installing

#### Clone this repo

```bash
git clone https://github.com/vile/discord-attendance-bot.git
cd discord-attendance-bot
```

#### Rename example .env file

```bash
mv .env.example .env
```

Put your bot's token in .env as `DISCORD_BOT_TOKEN`.
Put your guild's ID in .env as `GUILD_ID`.

#### Create venv

```bash
make venv
```

#### Install dependencies

```bash
make deps
```

#### Start the bot

```bash
make start
```

#### Sync Commands to Guild

To make application commands available in the server, mention the bot to invoke the `sync` text command.
Where `~` syncs all guild commands to the current guild (see: [command body](https://about.abstractumbra.dev/discord.py/2023/01/29/sync-command-example.html#command-body), [archive](https://archive.ph/vsSFz)).
Make sure the bot, temporarily, has `Send Messages` in the channel where you are mentioning the bot.

```
<@BOT_USER_ID> sync ~
```

If application commands are not synced to the guild, the bot integration will show that "this application has no commands," (rendering all commands unusable) and autocomplete will not work.

<details>
<summary>This application has no commands</summary>
<br>

![This application has no commands](./images/5-application-has-no-commands.jpg)

</details>

After the command tree has been synced, the bot no longer requires the `Send Messages` permission.

<details>
<summary>Properly synced commands</summary>
<br>

![Properly synced commands](./images/6-properly-synced-commands.jpg)

</details>

## Known Limitations

Since this bot is developed using [Python's shelve module](https://docs.python.org/3/library/shelve.html) for persistent data storage, there are some limitations intentionally imposed. 
Specifically, the retention of attendance session data (snapshots).
Snapshot data is permanently cleared when using the `/attendance clear` command, as well as on each bot start.
As such, instructors using this bot should immediately export an attendance report using the `/attendance get` command.

## Acknowledgements

- The [discord.py Discord](https://discord.com/invite/r3sSKJJ) and mod team for my answering questions
- [AbstractUmbra's](https://github.com/AbstractUmbra) open source command tree [syncing command](https://about.abstractumbra.dev/discord.py/2023/01/29/sync-command-example.html) ([The Unlicense](https://unlicense.org/))