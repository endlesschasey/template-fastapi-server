import logging

from app import app
from config.settings import config_setting

# 配置日志格式和级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config_setting.host, port=config_setting.port)