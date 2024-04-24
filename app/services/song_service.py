# app/services/song_service.py
from fastapi import Depends
from threading import Thread
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from sqlalchemy.orm import Session
from app.lib.suno import SunoApi, AudioInfo
from app.models.table import Song
from app.schemas.user import UserResponse
from app.schemas.song import *
from app.dependencies import get_db

class SongService:
    def __init__(self, db: Session = Depends(get_db), suno_api: SunoApi = Depends(SunoApi)):
        self.db = db
        self.suno_api = suno_api

    async def generate_and_wait(self, request: GenerateRequest, user: UserResponse) -> List[AudioInfo]:
        audios = await self.suno_api.generate(request.songDescription, request.songTitle, request.instrumentalState, True)
        Thread(target=self.save_songs, args=(audios, user, )).start()
        return audios

    async def custom_generate_and_wait(self, request: CustomGenerateRequest, user: UserResponse) -> List[AudioInfo]:
        audios = await self.suno_api.custom_generate(request.songLyrics, request.songStyles, request.songTitle, request.instrumentalState, True)
        Thread(target=self.save_songs, args=(audios, user,)).start()
        return audios

    async def get_song_list(self, request: SongListRequest, user: UserResponse) -> List[Song]:
        # 分页请求songs
        page_size = request.pageSize
        page_num = request.pageNum

        start = (page_num - 1) * page_size
        end = start + page_size
        songs = self.db.query(Song).filter(Song.user_id == user.id, Song.is_active == True).offset(start).limit(page_size).all()
        return {"songsList": songs, "total": len(songs)}

    async def get_song_info(self, request: SongInfoRequest, user: UserResponse) -> Song:
        song = self.db.query(Song).filter(Song.id == request.songId, Song.user_id == user.id, Song.is_active == True).first()
        return song

    async def delete_song(self, request: DeleteSongRequest, user: UserResponse):
        song = self.db.query(Song).filter(Song.id == request.songId, Song.user_id == user.id, Song.is_active == True).first()
        if song:
            song.is_active = False
            self.db.commit()
        return {"code": 200, "message": "success"}

    async def get_credits(self, user: UserResponse) -> Dict[str, Any]:
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())

        count = self.db.query(Song).filter(
            Song.user_id == user.id,
            Song.created_at >= today_start,
            Song.created_at <= today_end
        ).count()

        return {"Remaining": (6 - count) // 2}

    async def save_songs(self, audios: List[AudioInfo], user: UserResponse):
        for audio in audios:
            song = Song(
                user_id=user.id,
                studio_id=user.studio.id if user.studio else None,
                team_id=user.team.id if user.team else None,
                title=audio.title,
                image_url=audio.image_url,
                audio_url=audio.audio_url,
                video_url=audio.video_url,
                model_name=audio.model_name,
                gpt_description_prompt=audio.gpt_description_prompt,
                type=audio.type,
                prompt=audio.prompt,
                lyrics=audio.lyric,
                tags=audio.tags,
                make_instrumental=audio.duration is None,
                is_custom=audio.type == "custom"
            )
            self.db.add(song)
        self.db.commit()