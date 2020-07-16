
import pytest

from bot.controllers.command import Commands
from main import handle_content

from . import log_resp

PLATFORM = 'mgid'
test_command = Commands.widgets_low_cpa.value


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
async def test_command_with_help_flag():
    command = f'/{PLATFORM} {test_command} -h'
    data = await handle_content(command)
    assert log_resp(f'command: {command}\n\n{data}', f'help_command_with_help_flag.txt')
    assert 'arguments are required' in data