from pydantic import BaseModel, Field
from typing import Optional, List

from app.models.table import Song

class SongBase(BaseModel):
    title: Optional[str] = Field(default=None, description="Title of the song")
    image_url: Optional[str] = Field(default=None, description="URL of the song's image")
    audio_url: Optional[str] = Field(default=None, description="URL of the song's audio")
    tags: Optional[str] = Field(default=None, description="Tags describing the song")
    make_instrumental: Optional[bool] = Field(default=None, description="Whether the song is instrumental")

class SongResponse(SongBase):
    id: int = Field(description="Unique identifier of the song")

    @classmethod
    def from_orm(cls, song: Song):
        return cls(
            id=song.id,
            title=song.title,
            image_url=song.image_url,
            audio_url=song.audio_url,
            tags=song.tags,
            make_instrumental=song.make_instrumental,
        )

    class Config:
        from_attributes = True

class SongListResponse(BaseModel):
    songsList: List[SongResponse] = Field(description="List of songs")
    total: int = Field(description="Total number of songs")

class DeleteSongRequest(BaseModel):
    id: int = Field(description="Unique identifier of the song to be deleted")

class DeleteSongResponse(BaseModel):
    code: int = Field(description="Status code of the delete operation")
    message: str = Field(description="Message detailing the result of the delete operation")

class SongInfoRequest(BaseModel):
    id: int = Field(description="Unique identifier of the song for fetching details")

class SongInfoResponse(BaseModel):
    id: int = Field(description="Unique identifier of the song")
    image_url: str = Field(description="URL of the song's image")
    title: str = Field(description="Title of the song")
    tags: str = Field(description="Tags describing the song")
    created_at: str = Field(description="Creation date of the song")
    prompt: str = Field(description="Prompt used for creating the song")
    lyrics: str = Field(description="Lyrics of the song")

    @classmethod
    def from_orm(cls, song: Song):
        formatted_date = song.created_at.strftime('%Y-%m-%d %H:%M:%S') if song.created_at else None
        return cls(
            id=song.id,
            image_url=song.image_url,
            title=song.title,
            tags=song.tags,
            created_at=formatted_date,
            prompt=song.gpt_description_prompt,
            lyrics=song.lyrics,
        )

class CreditsResponse(BaseModel):
    credits: int = Field(description="Amount of credits available")

class GenerateRequest(BaseModel):
    songTitle: str = Field(description="Title of the song to be generated")
    songDescription: str = Field(description="Description of the song to be generated")
    instrumentalState: bool = Field(description="State if the song is instrumental or not")

class CustomGenerateRequest(BaseModel):
    songTitle: str = Field(description="Title of the song to be generated")
    songLyrics: str = Field(description="Lyrics of the song")
    songStyles: str = Field(description="Styles or genres of the song")
    instrumentalState: bool = Field(description="State if the song is instrumental or not")

class SongListRequest(BaseModel):
    pageSize: int = Field(description="Number of songs per page")
    pageNum: int = Field(description="Page number to fetch")


