from pydantic import BaseModel
from typing import Optional
from app.models.table import User


class StudioResponse(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True

class TeamResponse(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    name: str
    job_name: str
    job_number: str
    avatar_url: str
    is_active: bool
    studio: Optional[StudioResponse] = None
    team: Optional[TeamResponse] = None

    @classmethod
    def model_validate(cls, user: User):
        studio = None
        if user.teams:
            team = user.teams[0].team
            studio = StudioResponse.model_validate(team.studio)
            team = TeamResponse.model_validate(team)

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
                "studio":{
                    "id": 1,
                    "name": "Studio A"
                },
                "team":{
                    "id": 1,
                    "name": "Team A"
            }
        }
    }