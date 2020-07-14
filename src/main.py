import logging
import os
import traceback
import uuid
from datetime import datetime
from json import dump, dumps
from tempfile import NamedTemporaryFile
from textwrap import wrap
from typing import Union

import discord

from bot.controllers import MessageHandler
from errors import BaseCustomException

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

    logging.info(
        f'{client.user} is connected to the following guilds:\n'
        f'{guild.name}(id: {guild.id})\n'
        f'{guild_dev.name}(id: {guild_dev.id})\n'
    )
    now_format = datetime.now().strftime(r'%d.%m.%y, %H:%M:%S')
    if os.getenv('DEV'):
        logging.info(f'BOT Connected to {guild_dev.name}')
        await guild_dev.channel.send(f'[BOT-DEV] Connected. ({now_format})')
    else:
        logging.info(f'BOT Connected to {guild.name}')
        # await guild.channel.send(f'[BOT] Connected. ({now_format})')


async def handle_content(content):
    resp: Union[dict, list, str]
    output_format: Union['json', 'list', 'str', 'csv']
    try:
        resp, output_format = MESSAGE_HANDLER.handle_message(content)
        # for now - not doing anything with output_format, and asuming all responses are in str format.
    except Exception as err:
        err_resp = {
            "Response": "ERROR",
            "Type": "Internal Error",
        }
        if isinstance(err, BaseCustomException):
            logging.error(f'[!] ERROR: {err.dict()}')
            err_resp['message'] = err.message
        else:
            logging.error(f'[!] ERROR: {err}')
        traceback.print_tb(err.__traceback__)
        return err_resp

    return resp


@client.event
async def on_message(message):
    if message.guild.name not in [GUILD, GUILD_DEV]:
        return
    if os.getenv('DEV') and message.guild.name == GUILD:
        return
    elif message.guild.name == GUILD_DEV:
        return
    if message.author == client.user:  # ignore bot messages
        return
    _id = str(uuid.uuid4())[:4]  # new message id
    logging.debug(f'{_id} | FROM: {message.author} | MSG: {message.content}')
    resp = await handle_content(message.content)
    logging.debug(f'{_id} | RESP: {resp}')
    if resp.strip() == '':
        return await message.channel.send('Empty Results for Given Command'
                                          ' (Try Widening the Time-Interval for RequestedData)')
    if isinstance(resp, (list, dict)):
        resp_msg = dumps(resp, indent=2)
    else:
        resp_msg = resp
    if len(resp_msg) > MAX_NUMBER_LINES:
        # sends resp in multiple messages if exceeds tha max chars per message.
        for block_resp in wrap(resp_msg, MAX_NUMBER_LINES):
            await message.channel.send(block_resp)

        return
    await message.channel.send(resp_msg)


if __name__ == '__main__':
    client.run(TOKEN)
