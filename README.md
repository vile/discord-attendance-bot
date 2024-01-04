# Discord Attendance Bot

![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fvile%2Fdiscord-attendance-bot%2Fmaster%2Fpyproject.toml)
![Discord.py Package Version](https://img.shields.io/badge/discord.py-2.3.2-green)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)

A simple Discord bot for taking and reporting attendance of users within a specific voice channel. 

Originally created for [Boring Security DAO](https://twitter.com/BoringSecDAO).

## Requirements

1. Git - [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
   1. Check if you have Git installed with `git --version`
2. Python (>=3.10.12) - [Install Python (Windows)](https://www.python.org/downloads/windows/)
   1. Check if you have Python installed with `python3 --version`
3. Pip - [Install Pip](https://pip.pypa.io/en/stable/installation/)
   1. Check if you have Pip installed with `pip --version`

## Usage

### Creating a Discord Bot

This repo assumes you have created an application through the [Discord Dev Portal](https://discord.com/developers/applications) and attached a bot to it before.

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

You should put your Discord bot token in this .env file now

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