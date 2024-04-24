from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Tuple

from app.models.table import *
from app.schemas.user import *

def split_studio_team(dept: str):
    if ">" in dept:
        studio, team = dept.split(">")
        return studio, team
    else:
        return dept, None

def get_or_create_studio(db: Session, studio_name: str) -> Studio:
    studio = db.query(Studio).filter(Studio.name == studio_name).first()
    if studio is None:
        studio = Studio(name=studio_name)
        db.add(studio)
        db.flush()
    return studio

def get_or_create_team(db: Session, team_name: str, studio_id: int) -> Team:
    if team_name is None:
        return None
    team = db.query(Team).filter(Team.name == team_name, Team.studio_id == studio_id).first()
    if team is None:
        team = Team(name=team_name, studio_id=studio_id)
        db.add(team)
    return team

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
