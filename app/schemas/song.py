from pydantic import BaseModel
from typing import Optional, List

from app.models.table import Song

class CustomGenerateRequest(BaseModel):
    prompt: str
    tags: str
    title: str
    make_instrumental: bool = False
    wait_audio: bool = False

class GenerateLyricsRequest(BaseModel):
    prompt: str

class GenerateRequest(BaseModel):
    prompt: str
    make_instrumental: bool = False
    wait_audio: bool = False

class SongBase(BaseModel):
    title: Optional[str] = None
    ids: Optional[str] = None
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    model_name: Optional[str] = None
    gpt_description_prompt: Optional[str] = None
    type: Optional[str] = None
    prompt: Optional[str] = None
    lyrics: Optional[str] = None
    tags: Optional[str] = None
    make_instrumental: Optional[bool] = None
    is_custom: Optional[bool] = None

class SongResponse(SongBase):
    id: int
    is_active: bool
    
    @classmethod
    def from_orm(cls, song: Song):
        return cls(
            id=song.id,
            title=song.title,
            ids=song.ids,
            image_url=song.image_url,
            audio_url=song.audio_url,
            video_url=song.video_url,
            model_name=song.model_name,
            gpt_description_prompt=song.gpt_description_prompt,
            type=song.type,
            prompt=song.prompt,
            lyrics=song.lyrics,
            tags=song.tags,
            make_instrumental=song.make_instrumental,
            is_custom=song.is_custom,
            is_active=song.is_active
        )

    class Config:
        from_attributes = True

class GenerateRequest(BaseModel):
    songTitle: str
    songDescription: str
    instrumentalState: bool
    modelVersion: str = "chirp-v3-0"

class CustomGenerateRequest(BaseModel):
    songTitle: str
    songLyrics: str
    songStyles: str
    instrumentalState: bool
    modelVersion: str = "chirp-v3-0"

class SongResponse(BaseModel):
    id: str
    title: str
    tags: str
    image_url: str
    audio_url: str

class SongListRequest(BaseModel):
    pageSize: int
    pageNum: int

class SongListResponse(BaseModel):
    songsList: List[SongResponse]
    total: int

class DeleteSongRequest(BaseModel):
    songId: str

class DeleteSongResponse(BaseModel):
    code: int
    message: str

class SongInfoRequest(BaseModel):
    songId: str

class SongInfoResponse(BaseModel):
    id: str
    image_url: str
    title: str
    tags: str
    created_at: str
    prompt: str
    lyric: str

class GetCreditsResponse(BaseModel):
    credits: int