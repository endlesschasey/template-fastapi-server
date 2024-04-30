import logging
import colorlog
import random, asyncio
from typing import Optional


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建控制台处理器
handler = logging.StreamHandler()

# 设置具有多种颜色的日志格式
color_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s%(reset)s:     %(asctime)s%(reset)s - %(log_color)s%(message)s",
    datefmt="%Y-%m-%d  %H:%M:%S",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green,blue',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={
        'asctime': {
            'DEBUG': 'white',
            'INFO': 'white',
            'WARNING': 'white',
            'ERROR': 'white',
            'CRITICAL': 'white',
        }
    },
    reset=True
)

handler.setFormatter(color_formatter)

# 添加处理器到logger
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
