
import pytest

from bot.controllers.command import Commands
from tests import handle_content

from . import log_resp

PLATFORM = 'mgid'
test_command = Commands.widgets_low_cpa


@pytest.mark.asyncio
async def test_help_command():
    command = f'/help'
    data = await handle_content(command)
    assert log_resp(f'command: {command}\n\n{data}', f'help_program.txt')
    assert 'usage' in data.lower()


@pytest.mark.asyncio
async def test_help_platform_only():
    command = f'/{PLATFORM}'
    data = await handle_content(command)
    assert log_resp(f'command: {command}\n\n{data}', f'help_platform_only.txt')
    assert 'usage' in data.lower()


@pytest.mark.asyncio
async def test_help_in_args():
    command = f'/{PLATFORM} -h'
    data = await handle_content(command)
    assert log_resp(f'command: {command}\n\n{data}', f'help_in_args.txt')
    assert 'usage' in data.lower()


@pytest.mark.asyncio
async def test_command_missing_args():
    command = f'/{PLATFORM} {test_command}'
    data = await handle_content(command)
    assert log_resp(f'command: {command}\n\n{data}', f'help_command_missing_args.txt')
    assert 'usage:' in data


@pytest.mark.asyncio
async def test_command_with_help_flag():
    test_command = Commands.widgets_low_cpa
    command = f'/{PLATFORM} {test_command} -h'
    data = await handle_content(command)
    assert log_resp(f'command: {command}\n\n{data}', f'help_command_with_help_flag.txt')
    assert 'usage:' in data
    test_command = 'bot-traffic'
    command = f'/{PLATFORM} {test_command} -h'
    data = await handle_content(command)
    assert log_resp(f'command: {command}\n\n{data}', f'help_command_with_help_flag.txt')
    assert 'usage:' in data


@pytest.mark.asyncio
async def test_command_list_with_help_flag():
    command = f'/{PLATFORM} list -h'
    data = await handle_content(command)
    assert log_resp(f'command: {command}\n\n{data}', f'help_command_list_with_help_flag.txt')
    assert 'usage:' in data
