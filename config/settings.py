from dataclasses import dataclass
from dotenv import load_dotenv
import os

# 加载当前目录下的.env文件
load_dotenv()

@dataclass
class Setting:
    host = "192.168.30.144"
    port = 6699
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:shiyue@localhost:5432/MusicDB"
    COOKIE = os.environ.get("SUNO_COOKIE", "")

config_setting = Setting()