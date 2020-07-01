import logging
import os
import traceback
import uuid
from json import dump, dumps
from tempfile import NamedTemporaryFile
from textwrap import wrap
from typing import Union

import discord

from bot.controllers import MessageHandler
from errors import BaseCustomException

TOKEN = os.environ['DISCORD_TOKEN']
GUILD = os.environ['DISCORD_GUILD']
MESSAGE_HANDLER = MessageHandler()
client = discord.Client()
MAX_NUMBER_LINES = 2000


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )
    logging.info(f'Connected BOT to {guild.name}')


async def handle_content(content):
    resp: Union[dict, list, str]
    output_format: Union['json', 'list', 'str', 'csv']
    try:
        resp, output_format = MESSAGE_HANDLER.handle_message(content)
        # for now - not doing anything with output_format, and asuming all responses ar ein str format.
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
    if message.guild.name != GUILD:
        return
    if message.author == client.user:  # ignore bot messages
        return
    _id = str(uuid.uuid4())[:4]  # new message id
    logging.debug(f'{_id} | FROM: {message.author} | MSG: {message.content}')
    resp = await handle_content(message)
    logging.debug(f'{_id} | RESP: {resp}')
    if isinstance(resp, (list, dict)):
        resp_msg = dumps(resp, indent=2)
    else:
        resp_msg = resp
    if len(resp_msg) > MAX_NUMBER_LINES:
        # sends resp in multiple messages if exceeds tha max chars per message.
        for block_resp in wrap(resp_msg, MAX_NUMBER_LINES):
            await message.channel.send(block_resp)

            # with NamedTemporaryFile('w', delete=False, suffix='.json') as temp_file:
            #     dump(resp, temp_file, indent=2, ensure_ascii=False)
            #     # temp_file.write(resp_msg.encode())
            # await message.channel.send(
            #     f"Response Larger Than {MAX_NUMBER_LINES} Charactors. Response Attached as File.",
            #     file=discord.File(temp_file.name)
            # )
            # os.remove(temp_file.name)
        return

    await message.channel.send(resp_msg)

if __name__ == '__main__':
    client.run(TOKEN)
