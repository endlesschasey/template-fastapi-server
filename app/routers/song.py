# app/routers/song.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.song import (
    GenerateRequest, CustomGenerateRequest, SongResponse, 
    SongListRequest, SongListResponse, 
    DeleteSongRequest, DeleteSongResponse,
    SongInfoRequest, SongInfoResponse,
    GetCreditsResponse
)
from app.schemas.user import UserResponse
from app.dependencies import get_current_user
from app.services.song_service import SongService

router = APIRouter()

@router.post("/generate", response_model=list[SongResponse])
async def generate(
    request: GenerateRequest,
    current_user: UserResponse = Depends(get_current_user),
    song_service: SongService = Depends(SongService)
):
    songs = await song_service.generate_and_wait(request, current_user)
    if songs:
        return songs
    else:
        raise HTTPException(status_code=408, detail="Song generation timed out")

@router.post("/custom_generate", response_model=list[SongResponse])
async def custom_generate(
    request: CustomGenerateRequest,
    current_user: UserResponse = Depends(get_current_user),
    song_service: SongService = Depends(SongService)
):
    songs = await song_service.custom_generate_and_wait(request, current_user)
    if songs:
        return songs
    else:
        raise HTTPException(status_code=408, detail="Song generation timed out")

@router.get("/song_list", response_model=SongListResponse)
async def song_list(
    request: SongListRequest,
    current_user: UserResponse = Depends(get_current_user),
    song_service: SongService = Depends(SongService)
):
    songs_list, total = await song_service.get_song_list(request, current_user)
    return {"songsList": songs_list, "total": total}

@router.post("/delete_song", response_model=DeleteSongResponse)
async def delete_song(
    request: DeleteSongRequest,
    current_user: UserResponse = Depends(get_current_user),
    song_service: SongService = Depends(SongService)
):
    await song_service.delete_song(request, current_user)
    return {"code": 200, "message": "Song deleted successfully"}

@router.get("/song_info", response_model=SongInfoResponse)
async def song_info(
    request: SongInfoRequest,
    current_user: UserResponse = Depends(get_current_user),
    song_service: SongService = Depends(SongService)
):
    song_info = await song_service.get_song_info(request, current_user)
    return song_info

@router.get("/get_credits", response_model=GetCreditsResponse)
async def get_credits(
    current_user: UserResponse = Depends(get_current_user),
    song_service: SongService = Depends(SongService)
):
    credits = await song_service.get_credits(current_user)
    return credits