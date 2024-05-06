# app/routers/song.py
import os
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.schemas.song import *
from app.schemas.user import UserResponse
from app.dependencies import get_current_active_user, get_db
from app.services.song_service import SongService
from app.lib.utils import  logger

router = APIRouter()

@router.get("/get_file/{file_type}/{file_name}/{flag}")
async def get_file(file_type: str, file_name: str, flag: str = None, db: Session = Depends(get_db),):
    # 定义文件所在的目录
    base_dir = "OUTPUT"
    
    # 拼接文件路径
    file_path = os.path.join(base_dir, file_type, file_name)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=555, detail="File not found")
    
    # 如果flag为download，则记录日志
    if flag == "download":
        song_service = SongService()
        await song_service.log_download(db, file_name)
        
    # 返回文件响应
    return FileResponse(file_path)

# 生成歌曲
@router.post("/generate", response_model=list[SongResponse])
async def generate(
    generate_request: GenerateRequest = Body(...),
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Generates a new song based on provided details.
    """
    song_service = SongService()
    songs = await song_service.generate_and_wait(db, generate_request, current_user)
    songs = [SongResponse.from_orm(song) for song in songs]
    if songs:
        return songs
    else:
        raise HTTPException(status_code=408, detail="Song generation timed out")

# 自定义生成歌曲
@router.post("/custom_generate", response_model=list[SongResponse])
async def custom_generate(
    custom_generate_request: CustomGenerateRequest = Body(...),
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Generates a custom song based on provided details.
    """
    song_service = SongService()
    songs = await song_service.custom_generate_and_wait(db, custom_generate_request, current_user)
    songs = [SongResponse.from_orm(song) for song in songs]
    if songs:
        return songs
    else:
        raise HTTPException(status_code=408, detail="Custom song generation timed out")

# 获取歌曲列表
@router.post("/song_list", response_model=SongListResponse)
async def song_list(
    list_request: SongListRequest = Body(...),
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves a list of songs with pagination.
    """
    song_service = SongService()
    response = await song_service.get_song_list(db, list_request, current_user)
    return response

# 删除歌曲
@router.post("/delete_song", response_model=DeleteSongResponse)
async def delete_song(
    delete_request: DeleteSongRequest = Body(...),
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db),

):
    """
    Deletes a song based on the song ID.
    """
    song_service = SongService()
    response = await song_service.delete_song(db, delete_request, current_user)
    return response


# 获取歌曲信息
@router.post("/song_info", response_model=SongInfoResponse)
async def song_info(
    info_request: SongInfoRequest = Body(...),
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db),

):
    """
    Retrieves detailed information about a specific song.
    """
    song_service = SongService()
    song_info = await song_service.get_song_info(db, info_request, current_user)
    if not song_info:
        raise HTTPException(status_code=555, detail="Song not found")
    return song_info

# 获取积分
@router.get("/get_credits", response_model=CreditsResponse)
async def get_credits(
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db),

):
    """
    Retrieves the current user's credits.
    """
    song_service = SongService()
    credits = await song_service.get_credits(db, current_user)
    return credits
