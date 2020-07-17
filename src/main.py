import logging
import os
import traceback
import uuid
from datetime import datetime
from json import dump, dumps
from tempfile import NamedTemporaryFile
from typing import Union

import discord

from bot.controllers import MessageHandler
from errors import INTERNAL_ERROR_MSG, BaseCustomException, InvalidCommand
from extensions import helper_docs
from utils import groupify_list_strings

TOKEN = os.environ['DISCORD_TOKEN']
GUILD = os.environ['DISCORD_GUILD']
GUILD_DEV = os.environ['DISCORD_GUILD_DEV']
MESSAGE_HANDLER = MessageHandler()
client = discord.Client()
MAX_NUMBER_LINES = 2000


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)
    guild_dev = discord.utils.get(client.guilds, name=GUILD_DEV)
    channel_prod = [channel for channel in guild.channels if str(channel.type) == 'text'][0]
    channel_dev = [channel for channel in guild_dev.channels if str(channel.type) == 'text'][0]

    logging.info(
        f'{client.user} is connected to the following guilds:\n'
        f'{guild.name}(id: {guild.id})\n'
        f'{guild_dev.name}(id: {guild_dev.id})\n'
    )
    now_format = datetime.now().strftime(r'%d.%m.%y, %H:%M:%S')
    if os.getenv('DEV'):
        logging.info(f'BOT Connected to {guild_dev.name}')
        await channel_dev.send(f'[BOT-DEV] [{now_format}] Connected!')
    else:
        logging.info(f'BOT Connected to {guild.name}')
        # await channel_prod.send(f'[BOT] [{now_format}] Connected!')


async def handle_content(content):

    try:
        is_valid_command, args = helper_docs.parse_command(content)
        if not is_valid_command:
            help_message = args
            return help_message

        resp: Union[dict, list, str]
        output_format: Union['json', 'list', 'str', 'csv']
        resp, output_format = MESSAGE_HANDLER.handle_message(content)
        # for now - not doing anything with output_format, and asuming all responses are in str format.
    except InvalidCommand as err:
        resp = f"Invalid Command: {err.command}"
    except Exception as err:
        if isinstance(err, BaseCustomException):
            logging.error(f'[!] ERROR: {err.dict()}')
            INTERNAL_ERROR_MSG['message'] = err.message if hasattr(err, 'message') else str(err)
        else:
            logging.error(f'[!] ERROR: {err}')
        traceback.print_tb(err.__traceback__)
        resp = MESSAGE_HANDLER.format_response(INTERNAL_ERROR_MSG)
    return resp


@client.event
async def on_message(message):
    if message.guild.name not in [GUILD, GUILD_DEV]:
        return
    if message.guild.name == GUILD:  # response to specific channel (DEV or PROD)
        if os.getenv('DEV'):
            return
    if message.author == client.user:  # ignore bot messages
        return
    if not message.content.startswith('/'):  # ignore non-commands
        return

    try:
        resp = await handle_content(message.content.lower())
    except Exception as e:
        logging.error(e)
        resp = MESSAGE_HANDLER.format_response(INTERNAL_ERROR_MSG)

    if resp.strip() == '':
        return await message.channel.send('Empty Results for Given Command'
                                          ' (Try Widening the Time-Interval for RequestedData)')
    resp_msg = dumps(resp, indent=2) if isinstance(resp, (list, dict)) else resp
    if len(resp_msg) > MAX_NUMBER_LINES:
        # sends resp in multiple messages if exceeds tha max chars per message.
        for block_resp in groupify_list_strings(resp_msg.split('\n\n'), MAX_NUMBER_LINES, joiner='\n\n'):
            await message.channel.send(block_resp)
        return
    await message.channel.send(resp_msg)


if __name__ == '__main__':
    client.run(TOKEN)
