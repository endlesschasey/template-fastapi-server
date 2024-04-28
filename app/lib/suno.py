# lib/suno_api.py
import json, os, time
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from typing import Dict, Any, List, Optional

from .utils import logger, sleep, AudioInfo

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class SunoApi(metaclass=Singleton):
    BASE_URL: str = 'https://studio-api.suno.ai'
    CLERK_BASE_URL: str = 'https://clerk.suno.com'

    def __init__(self, cookie: str):
        if not hasattr(self, 'session'):
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
                'Cookie': cookie
            })
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"]  # 使用 allowed_methods 参数
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)

        if not hasattr(self, 'sid'):
            self.sid: Optional[str] = None

        if not hasattr(self, 'current_token'):
            self.current_token: Optional[str] = None

    async def init(self) -> 'SunoApi':
        await self.get_auth_token()
        await self.keep_alive()
        return self

    async def get_auth_token(self) -> None:
        get_session_url = f"{self.CLERK_BASE_URL}/v1/client?_clerk_js_version=4.72.0-snapshot.vc141245"
        session_response = self.session.get(get_session_url).json()
        if not session_response.get('response', {}).get('last_active_session_id'):
            raise Exception("Failed to get session id, you may need to update the SUNO_COOKIE")
        self.sid = session_response['response']['last_active_session_id']

    async def keep_alive(self, is_wait: bool = False) -> None:
        if not self.sid:
            raise Exception("Session ID is not set. Cannot renew token.")
        renew_url = f"{SunoApi.CLERK_BASE_URL}/v1/client/sessions/{self.sid}/tokens?_clerk_js_version=4.72.0-snapshot.vc141245"
        renew_response = self.session.post(renew_url).json()
        logger.info("KeepAlive...\n")
        if is_wait:
            logger.info("Before sleep")
            await sleep(1, 2)
            logger.info("After sleep")
        new_token = renew_response['jwt']
        self.current_token = new_token
        self.session.headers.update({'Authorization': f'Bearer {new_token}'})

    async def generate(self, prompt: str, title: str, make_instrumental: bool = False, wait_audio: bool = True) -> List[AudioInfo]:
        if not hasattr(self, 'current_token'):
            await self.get_auth_token()
        
        start_time = time.time()
        audios = await self.generate_songs(prompt, False, None, title, make_instrumental, wait_audio)
        cost_time = time.time() - start_time
        logger.info(f"Cost time: {cost_time}")
        return audios

    async def custom_generate(self, prompt: str, tags: str, title: str, make_instrumental: bool = False, wait_audio: bool = True) -> List[AudioInfo]:
        if not hasattr(self, 'current_token'):
            await self.get_auth_token()

        start_time = time.time()
        audios = await self.generate_songs(prompt, True, tags, title, make_instrumental, wait_audio)
        cost_time = time.time() - start_time
        logger.info(f"Cost time: {cost_time}")
        return audios

    async def generate_songs(self, prompt: str, is_custom: bool, tags: Optional[str], title: Optional[str], make_instrumental: Optional[bool], wait_audio: bool = False) -> List[AudioInfo]:
        await self.keep_alive(False)
        payload: Dict[str, Any] = {
            "make_instrumental": make_instrumental,
            "mv": "chirp-v3-0",
            "title": title,
            "prompt": "",
        }
        if is_custom:
            payload["tags"] = tags
            payload["prompt"] = prompt
        else:
            payload["gpt_description_prompt"] = prompt
        response = self.session.post(f"{SunoApi.BASE_URL}/api/generate/v2/", json=payload, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Error response: {response.text}")
        song_ids = [audio["id"] for audio in response.json()["clips"]]
        if wait_audio:
            start_time = time.time()
            last_response: List[AudioInfo] = []
            await sleep(5, 5)
            while time.time() - start_time < 100:
                response = await self.get(song_ids)
                all_completed = all(audio.status in ['complete'] for audio in response)
                if all_completed:
                    return response
                last_response = response
                await sleep(3, 6)
                await self.keep_alive(True)
            return last_response
        else:
            await self.keep_alive(True)
            return [AudioInfo(
                    id=audio["id"],
                    title=title,
                    image_url=audio.get("image_url"),
                    lyric=audio["metadata"].get("prompt", ""),
                    audio_url=audio.get("audio_url"),
                    video_url=audio.get("video_url"),
                    created_at=audio["created_at"],
                    model_name=audio["model_name"],
                    gpt_description_prompt=audio["metadata"].get("gpt_description_prompt"),
                    prompt=audio["metadata"].get("prompt"),
                    status=audio["status"],
                    type=audio["metadata"].get("type"),
                    tags=audio["metadata"].get("tags"),
                    duration=None  # Duration is not available in the clips data
                ) for audio in response.json()["clips"]]

    async def generate_lyrics(self, prompt: str) -> str:
        await self.keep_alive(False)
        generate_response = self.session.post(f"{SunoApi.BASE_URL}/api/generate/lyrics/", json={"prompt": prompt}).json()
        generate_id = generate_response["id"]
        lyrics_response = self.session.get(f"{SunoApi.BASE_URL}/api/generate/lyrics/{generate_id}").json()
        while lyrics_response.get("status") != "complete":
            await sleep(2)
            lyrics_response = self.session.get(f"{SunoApi.BASE_URL}/api/generate/lyrics/{generate_id}").json()
        return lyrics_response

    def parse_lyrics(self, prompt: str) -> str:
        lines = [line.strip() for line in prompt.split("\n") if line.strip()]
        return "\n".join(lines)

    async def get(self, song_ids: Optional[List[str]] = None) -> List[AudioInfo]:
        await self.keep_alive(False)
        url = f"{SunoApi.BASE_URL}/api/feed/"
        if song_ids:
            url = f"{url}?ids={','.join(song_ids)}"
        logger.info(f"Get audio status: {url}")
        response = self.session.get(url, timeout=3).json()
        return [AudioInfo(
            id=audio["id"],
            title=audio["title"],
            image_url=audio["image_url"],
            lyric=self.parse_lyrics(audio["metadata"]["prompt"]) if audio["metadata"]["prompt"] else "",
            audio_url=audio["audio_url"],
            video_url=audio["video_url"],
            created_at=audio["created_at"],
            model_name=audio["model_name"],
            status=audio["status"],
            gpt_description_prompt=audio["metadata"]["gpt_description_prompt"],
            prompt=audio["metadata"]["prompt"],
            type=audio["metadata"]["type"],
            tags=audio["metadata"]["tags"],
            duration=audio["metadata"]["duration"]
        ) for audio in response]

    async def get_credits(self) -> Dict[str, Any]:
        await self.keep_alive(False)
        response = self.session.get(f"{SunoApi.BASE_URL}/api/billing/info/").json()
        return {
            "credits_left": response["total_credits_left"],
            "period": response["period"],
            "monthly_limit": response["monthly_limit"],
            "monthly_usage": response["monthly_usage"]
        }

async def new_suno_api() -> SunoApi:
    cookie = os.environ.get("SUNO_COOKIE", "")
    suno_api = SunoApi()
    return await suno_api.init()
