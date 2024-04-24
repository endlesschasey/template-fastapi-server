from dataclasses import dataclass

@dataclass
class Setting:
    host = "192.168.30.144"
    port = 6699
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:shiyue@localhost:5432/MusicDB"


config_setting = Setting()