import logging
import asyncio
import random
from typing import Dict, Any, List, Optional


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class AudioInfo:
    def __init__(self, id: str, title: Optional[str], image_url: Optional[str], lyric: Optional[str],
                 audio_url: Optional[str], video_url: Optional[str], created_at: str, model_name: str,
                 gpt_description_prompt: Optional[str], prompt: Optional[str], status: str,
                 type: Optional[str], tags: Optional[str], duration: Optional[str]):
        self.id = id
        self.title = title
        self.image_url = image_url
        self.lyric = lyric
        self.audio_url = audio_url
        self.video_url = video_url
        self.created_at = created_at
        self.model_name = model_name
        self.gpt_description_prompt = gpt_description_prompt
        self.prompt = prompt
        self.status = status
        self.type = type
        self.tags = tags
        self.duration = duration

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "image_url": self.image_url,
            "lyric": self.lyric,
            "audio_url": self.audio_url,
            "video_url": self.video_url,
            "created_at": self.created_at,
            "model_name": self.model_name,
            "gpt_description_prompt": self.gpt_description_prompt,
            "prompt": self.prompt,
            "status": self.status,
            "type": self.type,
            "tags": self.tags,
            "duration": self.duration
        }

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