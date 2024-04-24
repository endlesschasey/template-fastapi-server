from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, Tuple, List

from app.models.table import *
from app.schemas.user import *

def split_studio_team(dept: str) -> Tuple[str, Optional[str]]:
    if ">" in dept:
        studio, team = dept.split(">")
        return studio.strip(), team.strip()
    else:
        return dept.strip(), None

def get_user(db: Session, user_info: dict) -> Tuple[UserResponse, bool]:
    try:
        name = user_info["alias"]
        user = db.query(User).filter(User.name == name).first()
        if user is None:
            user = User(
                name=name,
                job_number=user_info["username"],
                job_name=user_info["extra"]["job_name"],
                avatar_url=user_info["extra"]["avatar"],
            )
            db.add(user)

            studio_name, team_name = split_studio_team(user_info["dept"])
            studio = get_or_create_studio(db, studio_name)
            team = get_or_create_team(db, team_name, studio.id)
            db.commit()
            if team is not None:
                team_member = TeamMember(user_id=user.id, team_id=team.id)
                db.add(team_member)
        user.token = user_info["token"]
        user.job_name = user_info["extra"]["job_name"]
        user.avatar_url = user_info["extra"]["avatar"]
        db.commit()

        db.refresh(user)
        return UserResponse.model_validate(user)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to get or create user")

def get_or_create_studio(db: Session, studio_name: str) -> Studio:
    studio = db.query(Studio).filter(Studio.name == studio_name).first()
    if studio is None:
        studio = Studio(name=studio_name)
        db.add(studio)
        db.flush()
    return studio

def get_or_create_team(db: Session, team_name: Optional[str], studio_id: int) -> Optional[Team]:
    if team_name is None:
        return None
    team = db.query(Team).filter(Team.name == team_name, Team.studio_id == studio_id).first()
    if team is None:
        team = Team(name=team_name, studio_id=studio_id)
        db.add(team)
    return team

def create_or_update_user(db: Session, user_info: dict) -> UserResponse:
    try:
        name = user_info["alias"]
        user = db.query(User).filter(User.name == name).first()
        if user is None:
            user = User(
                name=name,
                job_number=user_info["username"],
                job_name=user_info["extra"]["job_name"],
                avatar_url=user_info["extra"]["avatar"],
                token=user_info["token"],
            )
            db.add(user)
        else:
            user.job_name = user_info["extra"]["job_name"]
            user.avatar_url = user_info["extra"]["avatar"]
            user.token = user_info["token"]

        studio_name, team_name = split_studio_team(user_info["dept"])
        studio = get_or_create_studio(db, studio_name)
        team = get_or_create_team(db, team_name, studio.id)
        db.commit()

        if team is not None:
            team_member = db.query(TeamMember).filter(TeamMember.user_id == user.id, TeamMember.team_id == team.id).first()
            if team_member is None:
                team_member = TeamMember(user_id=user.id, team_id=team.id)
                db.add(team_member)
                db.commit()

        db.refresh(user)
        return UserResponse.model_validate(user)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to create or update user")

def get_user_by_id(db: Session, user_id: int) -> Optional[UserResponse]:
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        return None
    return UserResponse.model_validate(user)

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserResponse]:
    users = db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(user) for user in users]

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    user_data = user_update.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)

def delete_user(db: Session, user_id: int) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    user.is_active = False
    db.commit()
    db.refresh(user)
    return user