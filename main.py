from app import app
from config.settings import config_setting

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config_setting.host, port=config_setting.port)