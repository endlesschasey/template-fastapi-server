# app/services/song_service.py
import os, threading
from tqdm import tqdm
import requests, asyncio
from concurrent.futures import ThreadPoolExecutor, Future
from typing import List
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.lib.suno import SunoApi, AudioInfo
from app.lib.utils import logger
from app.models.table import Song, Log
from app.schemas.user import UserResponse
from app.schemas.song import *
from config.settings import Setting

class SongService:
    def __init__(self, max_concurrent_tasks: int=2):
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def generate_and_wait(self, db: Session, request: GenerateRequest, user: UserResponse) -> List[dict]:
        async with self.semaphore:
            suno_api = await SunoApi(cookie=Setting.COOKIE).init()
            logger.info(f"Generating song with description: {request.songDescription}")
            audios = await suno_api.generate(request.songDescription, request.songTitle, request.instrumentalState, True)
            
            # 创建一个新的线程来执行 save_songs 方法
            save_thread = threading.Thread(target=self.save_songs, args=(db, request.songTitle, audios, user, ))
            save_thread.start()
            
            # 等待线程完成
            save_thread.join()
            
            songs = db.query(Song).filter(Song.title == request.songTitle, Song.user_id == user.id).order_by(Song.id.desc()).limit(2).all()
            for song in songs:
                db.refresh(song)
            return songs

    async def custom_generate_and_wait(self, db: Session, request: CustomGenerateRequest, user: UserResponse) -> List[dict]:
        async with self.semaphore:
            suno_api = await SunoApi(cookie=Setting.COOKIE).init()
            logger.info(f"Generating custom song with lyrics: {request.songLyrics}")
            audios = await suno_api.custom_generate(request.songLyrics, request.songStyles, request.songTitle, request.instrumentalState, True)
            
            # 创建一个新的线程来执行 save_songs 方法
            save_thread = threading.Thread(target=self.save_songs, args=(db, request.songTitle, audios, user, ))
            save_thread.start()
            
            # 等待线程完成
            save_thread.join()
            
            songs = db.query(Song).filter(Song.title == request.songTitle, Song.user_id == user.id).order_by(Song.id.desc()).limit(2).all()
            for song in songs:
                db.refresh(song)
            return songs

    async def get_song_list(self, db: Session, request: SongListRequest, user: UserResponse) -> SongListResponse:
        page_size = request.pageSize
        page_num = request.pageNum

        start = (page_num - 1) * page_size
        logger.info(f"Fetching song list for user {user.name}, page {page_num}")
        songs = db.query(Song).filter(Song.user_id == user.id, Song.is_active == True).order_by(Song.id.desc()).offset(start).limit(page_size).all()
        total = db.query(Song).filter(Song.user_id == user.id, Song.is_active == True).count()
        # Convert Song DB models to SongResponse models
        songs_response = [SongResponse.from_orm(song) for song in songs]  # Adjust as per the actual Song model attributes

        # Prepare and return the response using the Pydantic model
        response = SongListResponse(songsList=songs_response, total=total)
        return response

    async def get_song_info(self, db: Session, request: SongInfoRequest, user: UserResponse) -> SongInfoResponse:
        logger.info(f"Fetching song info for song {request.id}, user {user.name}")
        song = db.query(Song).filter(Song.id == request.id, Song.user_id == user.id, Song.is_active == True).first()
        if not song:
            return None
        return SongInfoResponse.from_orm(song)

    async def log_download(self, db: Session, file_name: str):
        logger.info(f"Logging download for file {file_name}")
        song = db.query(Song).filter(Song.audio_url.contains(file_name)).first()
        if song:
            log = Log(song_id=song.id, user_id=song.user_id, action="download", message=f"User downloaded song {song.title}")
            db.add(log)
            db.commit()

    async def delete_song(self, db: Session, request: DeleteSongRequest, user: UserResponse) -> DeleteSongResponse:
        logger.info(f"Deleting song {request.id} for user {user.name}")
        song = db.query(Song).filter(Song.id == request.id, Song.user_id == user.id, Song.is_active == True).first()
        if song:
            song.is_active = False
            db.commit()
            return DeleteSongResponse(code=200, message="Song deleted successfully")
        return DeleteSongResponse(code=555, message="Song not found")

    async def publish_song(self, db: Session, request: PublishSongRequest, user: UserResponse) -> PublishSongResponse:
        logger.info(f"Publishing song {request.id} for user {user.name}")
        song = db.query(Song).filter(Song.id == request.id, Song.user_id == user.id, Song.is_active == True).first()
        if song:
            song.is_public = True
            db.commit()
            return PublishSongResponse(code=200, message="Song published successfully")
        return PublishSongResponse(code=555, message="Song not found")

    async def get_credits(self, db: Session, user: UserResponse) -> CreditsResponse:
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        logger.info(f"Fetching credits for user {user.name}")
        count = db.query(Song).filter(
            Song.user_id == user.id,
            Song.created_at >= today_start,
            Song.created_at <= today_end
        ).count()
        
        return CreditsResponse(credits=((10 - count) // 2))

    @staticmethod
    def download_file(url: str, output_path: str) -> None:
        logger.info(f"Downloading file from {url} to {output_path}")
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("Content-Length", 1024*1500))
        block_size = 1024  # 1 KB

        with open(output_path, "wb") as f:
            with tqdm(
                desc=os.path.basename(output_path),
                total=total_size,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
                colour="blue",
                leave=True,
            ) as progress_bar:
                for data in response.iter_content(block_size):
                    size = f.write(data)
                    progress_bar.update(size)
                    progress_bar.set_postfix(file=os.path.basename(output_path), refresh=True)

    def download_files(self, audios: List[AudioInfo]) -> None:
        logger.info("Downloading audio and image files")
        with ThreadPoolExecutor() as executor:
            futures: List[Future] = []
            for audio in audios:
                if audio.image_url is None or audio.audio_url is None:
                    continue
                image_filename = f'{audio.image_url.split("image_")[1]}'
                image_path = os.path.join("OUTPUT", "images", image_filename)
                os.makedirs(os.path.dirname(image_path), exist_ok=True)

                if "=" in audio.audio_url:
                    audio_filename = f'{audio.audio_url.split("=")[1]}.mp3'
                else:
                    audio_filename = f'{audio.audio_url.split("-")[-1]}'
                audio_path = os.path.join("OUTPUT", "audios", audio_filename)
                os.makedirs(os.path.dirname(audio_path), exist_ok=True)

                futures.append(executor.submit(self.download_file, audio.image_url, image_path))
                futures.append(executor.submit(self.download_file, audio.audio_url, audio_path))

            # 等待所有任务完成
            for future in futures:
                future.result()

    def save_songs(self, db: Session, title: str, audios: List[AudioInfo], user: UserResponse) -> None:
        logger.info(f"Saving songs with title: {title}")
        try:
            self.download_files(audios)

            for audio in audios:
                if audio.image_url is None or audio.audio_url is None:
                    continue
                image_filename = f'{audio.image_url.split("image_")[1]}'
                if "=" in audio.audio_url:
                    audio_filename = f'{audio.audio_url.split("=")[1]}'
                else:
                    audio_filename = f'{audio.audio_url.split("-")[-1]}'
                if ".mp3" not in audio_filename:
                    audio_filename += ".mp3"

                # 构建接口的 URL
                image_url = f"/api/get_file/images/{image_filename}"
                audio_url = f"/api/get_file/audios/{audio_filename}"

                song = Song(
                    user_id=user.id,
                    studio_id=user.studio.id if user.studio else None,
                    team_id=user.team.id if user.team else None,
                    title=title,
                    image_url=image_url,
                    audio_url=audio_url,
                    video_url=audio.video_url,
                    model_name=audio.model_name,
                    gpt_description_prompt=audio.gpt_description_prompt,
                    type=audio.type,
                    prompt=audio.prompt,
                    lyrics=audio.lyric,
                    tags=audio.tags,
                    created_at=datetime.now(),
                    make_instrumental=audio.lyric is None,
                    is_custom=audio.type == "custom"
                )
                db.add(song)
            db.commit()
        except Exception as e:
            db.rollback()  # 在异常发生时回滚
            logger.error(f"Error saving songs: {e}")
            raise e