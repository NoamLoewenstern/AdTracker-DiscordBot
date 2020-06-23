import logging
import os
import uuid
from json import dump, dumps
from tempfile import NamedTemporaryFile
from typing import Union

import discord

from bot.controller import MessageHandler

TOKEN = os.environ['DISCORD_TOKEN']
GUILD = os.environ['DISCORD_GUILD']
MESSAGE_HANDLER = MessageHandler()
client = discord.Client()


@client.event
async def on_ready():
    guild = discord.utils.get(client.guilds, name=GUILD)

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )
    logging.info(f'Connected BOT to {guild.name}')


@client.event
async def on_message(message):
    if message.guild.name != GUILD:
        return
    if message.author == client.user:  # ignore bot messages
        return
    _id = str(uuid.uuid4())[:4]  # new message id
    logging.debug(f'{_id} | FROM: {message.author} | MSG: {message.content}')
    resp: Union[dict, list, str] = MESSAGE_HANDLER.handle_message(message.content)
    logging.debug(f'{_id} | RESP: {resp}')
    if isinstance(resp, (list, dict)):
        resp_msg = dumps(resp, indent=2)
    else:
        resp_msg = resp
    if len(resp_msg) > 2000:
        with NamedTemporaryFile('w', delete=False, suffix='.json') as temp_file:
            dump(resp, temp_file, indent=2, ensure_ascii=False)
            # temp_file.write(resp_msg.encode())
        await message.channel.send(
            "Response Larger Than 2000 Charactors. Response Attached as File.",
            file=discord.File(temp_file.name)
        )
        os.remove(temp_file.name)
        return

    await message.channel.send(resp_msg)


if __name__ == '__main__':
    client.run(TOKEN)
