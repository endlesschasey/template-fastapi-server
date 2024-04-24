from sqlalchemy import create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pytz import timezone

from config.settings import config_setting

class BeijingDateTime(DateTime):
    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.astimezone(timezone('Asia/Shanghai'))
        return value

try:
    engine = create_engine(config_setting.SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    print(e)
    exit(1)

