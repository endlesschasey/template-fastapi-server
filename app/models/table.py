from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.utils.database import Base, BeijingDateTime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True) # 姓名
    job_number = Column(String, unique=True, index=True) # 工号
    job_name = Column(String) # 职位
    token = Column(String) # OA token
    avatar_url = Column(String) # 个人头像
    created_at = Column(BeijingDateTime, default=datetime.now()) # 加入时间

    teams = relationship("TeamMember", back_populates="user")
    articles = relationship("Article", back_populates="author")

    is_active = Column(Boolean, default=True)

class Studio(Base):
    __tablename__ = "studios"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True) # 一级项目组

    teams = relationship("Team", back_populates="studio")

    is_active = Column(Boolean, default=True)

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True) # 二级工作室
    studio_id = Column(Integer, ForeignKey("studios.id"))

    studio = relationship("Studio", back_populates="teams")
    members = relationship("TeamMember", back_populates="team")

    is_active = Column(Boolean, default=True)

class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))

    user = relationship("User", back_populates="teams")
    team = relationship("Team", back_populates="members")

    __table_args__ = (
        UniqueConstraint('user_id', 'team_id', name='unique_user_team'),
    )
