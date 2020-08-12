import sys
from pathlib import Path


src_folder = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_folder))

async def handle_content(command: str) -> str:
    from src.main import MESSAGE_HANDLER, handle_content as main_handle_content
    main_resp, main_error_resp = await main_handle_content(command)
    full_resp = main_resp
    if main_error_resp:
        full_resp += f'\n\nERRORS:\n{main_error_resp}'
    return full_resp.strip()
