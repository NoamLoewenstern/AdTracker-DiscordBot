import logging
import os
import traceback
import uuid
from datetime import datetime
from json import dump, dumps
from tempfile import NamedTemporaryFile
from typing import Dict, List, Tuple, Union

import discord
from discord import channel

from bot.controllers.message import MessageHandler, OutputFormatTypes
from constants import DEBUG, DEV
from errors import (BaseCustomException, ErrorList, InternalError,
                    InvalidCommandError)
from errors.platforms import CampaignNameMissingTrackerIDError
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
    if DEV:
        logging.info(f'BOT Connected to {guild_dev.name}')
        await channel_dev.send(f'[BOT-DEV] [{now_format}] Connected!')
    else:
        logging.info(f'BOT Connected to {guild.name}')
        # await channel_prod.send(f'[BOT] [{now_format}] Connected!')


def format_resp(resp: Union[str, List[Union[str, Dict[str, str]]]]) -> str:
    return MESSAGE_HANDLER.format_response(resp)


def format_error_resp(list_error_resp: Union[str, List[Union[str, Dict[str, str]]]]) -> str:
    if isinstance(list_error_resp, str):
        return list_error_resp
    if isinstance(list_error_resp, list):
        if len(list_error_resp) == 0:
            return ''  # if len is 0 and is a list.
        if isinstance(list_error_resp[0], str):
            return '\n\n'.join(list_error_resp)

    errors_by_message_dict = {}
    other_errors = []
    for error in list_error_resp:
        # filter null values
        error = {key: value for key, value in error.items() if value and value != 'None'}
        if (err_msg := error.get('message')):
            del error['message']
            errors_by_message_dict.setdefault(err_msg, []).append(error)
        else:
            other_errors.append({error})
    formatted_error = []
    for err_msg in sorted(errors_by_message_dict):
        list_errors = errors_by_message_dict[err_msg]
        formatted_error.append('{}:\n{}'.format(err_msg, MESSAGE_HANDLER.format_response(list_errors)))
    if other_errors:
        formatted_error.append('{}:\n{}'.format('Other Errors',
                                                MESSAGE_HANDLER.format_response(other_errors)))
    ret_error_resp = MESSAGE_HANDLER.format_response('\n\n'.join(formatted_error))
    return ret_error_resp


async def handle_content(content: str) -> Tuple[str]:
    try:
        is_valid_command, args = helper_docs.parse_command(content)
        if not is_valid_command:
            help_message = args
            return help_message, ErrorList()

        resp: Union[dict, list, str]
        output_format: OutputFormatTypes
        resp, error_resp, output_format = MESSAGE_HANDLER.handle_message(content, format_output=False)
        # for now - not doing anything with output_format, and asuming all responses are in str format.
    except InvalidCommandError as err:
        resp = ''
        error_resp = f"Invalid Command: {err.command}"
    except CampaignNameMissingTrackerIDError as err:
        resp = ''
        error_resp = MESSAGE_HANDLER.format_response(err.dict())
    except Exception as err:
        internal_error = InternalError(message=getattr(err, 'message', str(err)))
        # -> if isinstance BaseCustomException
        logging.error(f'[!] ERROR: {getattr(err, "dict", lambda: None)()}')
        traceback.print_tb(err.__traceback__)
        resp = ''
        error_resp = MESSAGE_HANDLER.format_response(internal_error.dict())

    resp, error_resp = format_resp(resp), format_error_resp(error_resp)
    if resp.strip() == '' and error_resp.strip() == '':
        resp = 'Empty Results for Given Command (Try Widening the Time-Interval for RequestedData)'

    return resp, error_resp


async def send_msg(channel, msg: str) -> None:
    if len(msg) > MAX_NUMBER_LINES:
        # sends resp in multiple messages if exceeds tha max chars per message.
        for block_resp in groupify_list_strings(msg.split('\n\n'), MAX_NUMBER_LINES, joiner='\n\n'):
            await channel.send(block_resp)
        return
    await channel.send(msg)


@client.event
async def on_message(message):
    if message.guild.name not in [GUILD, GUILD_DEV]:
        return
    # response to specific channel (DEV or PROD)
    if DEV and message.guild.name == GUILD \
            or not DEV and message.guild.name == GUILD_DEV:
        return
    if message.author == client.user:  # ignore bot messages
        return
    if not message.content.startswith('/'):  # ignore non-commands
        return

    try:
        resp, error_resp = await handle_content(message.content.lower())
    except Exception as e:
        logging.error(e)
        resp = ''
        error_resp = MESSAGE_HANDLER.format_response(InternalError.dict())

    # resp = dumps(resp, indent=2) if isinstance(resp, (list, dict, tuple)) else resp
    # error_resp = dumps(error_resp, indent=2) if isinstance(error_resp, (list, dict, tuple)) else resp

    if resp:
        await send_msg(message.channel, resp)
    if error_resp:
        await send_msg(message.channel, '__*ERRORS:*__\n' + error_resp)


if __name__ == '__main__':
    client.run(TOKEN)
