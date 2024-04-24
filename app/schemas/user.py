from pydantic import BaseModel
from typing import Optional
from app.models.table import User, Studio, Team

class StudioResponse(BaseModel):
    id: int
    name: str

    @classmethod
    def from_orm(cls, studio: Studio):
        return cls(id=studio.id, name=studio.name)

class TeamResponse(BaseModel):
    id: int
    name: str

    @classmethod
    def from_orm(cls, team: Team):
        return cls(id=team.id, name=team.name)

class UserBase(BaseModel):
    name: Optional[str] = None
    job_name: Optional[str] = None
    job_number: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    name: str
    job_number: str

class UserUpdate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_active: bool
    studio: Optional[StudioResponse] = None
    team: Optional[TeamResponse] = None

    @classmethod
    def from_orm(cls, user: User):
        studio = None
        team = None
        if user.teams:
            team_member = user.teams[0]
            team = TeamResponse.from_orm(team_member.team)
            studio = StudioResponse.from_orm(team_member.team.studio)

        return cls(
            id=user.id,
            name=user.name,
            job_name=user.job_name,
            job_number=user.job_number,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            studio=studio,
            team=team
        )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "job_name": "Developer",
                "job_number": "E1234",
                "avatar_url": "https://example.com/avatar.jpg",
                "is_active": True,
                "studio": {
                    "id": 1,
                    "name": "Studio A"
                },
                "team": {
                    "id": 1,
                    "name": "Team A"
                }
            }
        }