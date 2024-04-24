from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, UniqueConstraint
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

    power = Column(Integer, default=0)

    teams = relationship("TeamMember", back_populates="user")
    articles = relationship("Article", back_populates="author")
    songs = relationship("Song", back_populates="created_by")

    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}')>"

class Studio(Base):
    __tablename__ = "studios"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True) # 一级项目组

    teams = relationship("Team", back_populates="studio")

    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Studio(id={self.id}, name='{self.name}')>"

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True) # 二级工作室
    studio_id = Column(Integer, ForeignKey("studios.id", ondelete="CASCADE"))

    studio = relationship("Studio", back_populates="teams")
    members = relationship("TeamMember", back_populates="team")

    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}')>"

class TeamMember(Base):
    __tablename__ = "team_members"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), primary_key=True)

    user = relationship("User", back_populates="teams")
    team = relationship("Team", back_populates="members")


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    studio_id = Column(Integer, ForeignKey("studios.id", ondelete="CASCADE"))
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"))

    title = Column(String)

    image_url = Column(String)
    audio_url = Column(String)
    video_url = Column(String)
    model_name = Column(String)  
    gpt_description_prompt = Column(Text) 
    type = Column(String)
    prompt = Column(String) # 歌曲描述
    lyrics = Column(Text) # 歌词
    tags = Column(String) # 风格标签
    make_instrumental = Column(Boolean, default=False) # 是否为纯音乐
    is_custom = Column(Boolean, default=False) # 是否为自定义
    
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  
    created_at = Column(BeijingDateTime, default=datetime.now())
    deleted_at = Column(BeijingDateTime)

    created_by = relationship("User", back_populates="songs")

    def __repr__(self):
        return f"<Song(id={self.id}, title='{self.title}')>"