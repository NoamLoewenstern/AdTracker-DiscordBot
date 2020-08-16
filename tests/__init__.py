import sys
from pathlib import Path


src_folder = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_folder))

async def handle_content(command: str) -> str:
    from src.main import handle_content as main_handle_content
    result = await main_handle_content(command)
    main_resp = result['resp']
    main_error_resp = result['error_res']
    full_resp = main_resp
    if main_error_resp:
        full_resp += f'\n\nERRORS:\n{main_error_resp}'
    return full_resp.strip()
