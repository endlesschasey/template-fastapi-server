import logging
import asyncio
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

async def sleep(x: int, y: int = None) -> None:
    """
    Pause for a specified number of seconds.
    
    :param x: Minimum number of seconds.
    :param y: Maximum number of seconds (optional).
    """
    timeout = x
    if y is not None and y != x:
        min_val = min(x, y)
        max_val = max(x, y)
        timeout = random.randint(min_val, max_val)
    
    await asyncio.sleep(timeout)

cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}