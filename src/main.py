import os
import traceback
import uuid
from datetime import datetime
from json import dump, dumps
from tempfile import NamedTemporaryFile
from time import sleep
from typing import Dict, List, Tuple, Union

import discord

from bot.controllers.message import MessageHandler, OutputFormatTypes
from config import DEBUG_COMMAND_FLAG, RUNNING_ON_SERVER
from constants import DEBUG, DEV
from errors import (BaseCustomException, ErrorList, InternalError,
                    InvalidCommandError, PydanticParseObjError)
from errors.network import APIError, AuthError
from errors.platforms import (CampaignNameMissingTrackerIDError,
                              InvalidCampaignIDError)
from extensions import helper_docs
from logger import logger
from utils import (GENERAL_RESP_TYPE, convert_list_dicts_to_csv_file,
                   groupify_list_strings)

TOKEN = os.environ['DISCORD_TOKEN']
GUILD = os.environ['DISCORD_GUILD']
GUILD_DEV = os.environ['DISCORD_GUILD_DEV']
MESSAGE_HANDLER = MessageHandler()
client = discord.Client()
MAX_NUMBER_LINES = 2000


@client.event
async def on_ready():
    start_msg = 'STARTED BOT LISTENING ON ' + 'DEV' if DEV else 'PROD'
    print(start_msg)
    logger.info(start_msg)

    guild = discord.utils.get(client.guilds, name=GUILD)
    guild_dev = discord.utils.get(client.guilds, name=GUILD_DEV)
    channel_prod = [channel for channel in guild.channels if str(channel.type) == 'text'][0]
    channel_dev = [channel for channel in guild_dev.channels if str(channel.type) == 'text'][0]

    logger.info(
        f'{client.user} is connected to the following guilds:\n'
        f'{guild.name}(id: {guild.id})\n'
        f'{guild_dev.name}(id: {guild_dev.id})\n'
    )
    now_format = datetime.now().strftime(r'%d.%m.%y, %H:%M:%S')
    if DEV:
        logger.info(f'BOT Connected to {guild_dev.name}')
        await channel_dev.send(f'[BOT-DEV] [{now_format}] Connected!')
    else:
        logger.info(f'BOT Connected to {guild.name}')
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


async def handle_content(command: str) -> Tuple[str]:
    try:

        is_valid_command, args = helper_docs.parse_command(command)
        if not is_valid_command:
            help_message = args
            return help_message, ErrorList()

        resp: Union[dict, list, str]
        output_format: OutputFormatTypes
        resp, error_resp, output_format = MESSAGE_HANDLER.handle_message(command, format_output=False)
        # for now - not doing anything with output_format, and asuming all responses are in str format.
    except InvalidCommandError as err:
        resp = ''
        error_resp = f"Invalid Command: {err.command}"
    except (CampaignNameMissingTrackerIDError, APIError, AuthError, InvalidCampaignIDError,
            PydanticParseObjError, BaseCustomException) as err:
        resp = ''
        error_resp = MESSAGE_HANDLER.format_response(err.dict())
        if not RUNNING_ON_SERVER:
            traceback.print_tb(err.__traceback__)
    except Exception as err:
        err_msg = getattr(err, 'message', getattr(err, 'data', str(err)))
        internal_error = InternalError(message=err_msg)
        # -> if isinstance BaseCustomException
        logger.error(f'[!] ERROR: {internal_error.dict()}')
        if not RUNNING_ON_SERVER:
            traceback.print_tb(err.__traceback__)
        resp = ''
        error_resp = MESSAGE_HANDLER.format_response(internal_error.dict())

    orig_resp, orig_error_resp = resp, error_resp
    resp, error_resp = format_resp(resp), format_error_resp(error_resp)
    if resp.strip() == '' and error_resp.strip() == '':
        resp = 'Empty Results for Given Command (Try Widening the Time-Interval for RequestedData)'

    return {
        'resp': resp,
        'error_resp': error_resp,
        'orig_resp': orig_resp,
        'orig_error_resp': orig_error_resp,
    }


async def send_msg(channel, msg: str, orig_resp: GENERAL_RESP_TYPE) -> None:
    try:
        if len(msg) > MAX_NUMBER_LINES * 2:
            csv_file = convert_list_dicts_to_csv_file(orig_resp)
            return await channel.send(file=discord.File(str(csv_file)))
    except:
        pass
    try:
        if len(msg) > MAX_NUMBER_LINES:
            # sends resp in multiple messages if exceeds tha max chars per message.
            for block in groupify_list_strings(msg.strip().split('\n\n'), MAX_NUMBER_LINES, joiner='\n\n'):
                if block:
                    await channel.send(block)
                else:
                    print(f'Trying sending Empty messge: {block}')
            return
        return await channel.send(msg)
    except Exception as e:
        err_msg = f'Internal Error - Unexpected: {e}\n{traceback.format_exc()}'
        try:
            print(err_msg)
            return await channel.send(err_msg)
        except Exception as e:
            sec_err_msg = ('=' * 10) + '\n'
            sec_err_msg += 'AGAIN ERROR - CANNOT SEND MESSAGES TO DISCORD CHANNEL'
            sec_err_msg += '\n' + ('=' * 10)
            sec_err_msg += '\n' + 'Message Tried to Send:\n'
            sec_err_msg += msg
            print(sec_err_msg)


@ client.event
async def on_message(message):
    if message.author == client.user:  # ignore bot messages
        return
    guild_name = message.guild.name
    if guild_name not in [GUILD, GUILD_DEV]:
        return
    # DEBUG
    command = message.content
    if DEBUG_COMMAND_FLAG in command:
        if RUNNING_ON_SERVER:
            return
        command = command.replace(DEBUG_COMMAND_FLAG, '').strip()
    # response to specific channel (DEV or PROD)
    if guild_name == GUILD_DEV and not DEV \
            or guild_name == GUILD and DEV:
        return
    if not command.startswith('/'):  # ignore non-commands
        return

    result = {}
    try:
        result = await handle_content(command)
        if isinstance(result, tuple):
            result = {
                'resp': result[0],
                'error_resp': result[1],
                'orig_resp': result[0],
                'orig_error_resp': result[1],
            }
    except Exception as e:
        logger.error(e)
        result['resp'] = ''
        result['error_resp'] = MESSAGE_HANDLER.format_response(InternalError.dict())

    if result['resp']:
        await send_msg(message.channel, result['resp'], result['orig_resp'])
    if result['error_resp']:
        sleep(0.5)
        await send_msg(message.channel, '__*ERRORS:*__\n' + result['error_resp'], result['orig_error_resp'])


if __name__ == '__main__':
    client.run(TOKEN)
