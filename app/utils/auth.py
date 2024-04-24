import base64
import hmac
import logging
from hashlib import sha256
from typing import Optional, Union

import requests

is_user = False

logger = logging.getLogger(__name__)

def get_signature(data: str, secret: str) -> bytes:
    secret = secret.encode('utf-8')
    data = data.encode('utf-8')
    return hmac.new(secret, data, digestmod=sha256).digest()


def base64_url_decode(data: str) -> bytes:
    remainder = len(data) % 4
    if remainder > 0:
        data += "=" * (4 - remainder)
    return base64.b64decode(data.replace('-', '+').replace('_', '/'))


def verify(token: str, secret: str) -> Optional[str]:
    jwt_arr = token.split('.')
    if len(jwt_arr) != 3:
        return None

    signature = get_signature(jwt_arr[0] + '.' + jwt_arr[1], secret)
    if signature == base64_url_decode(jwt_arr[2]):
        return base64_url_decode(jwt_arr[1]).decode('utf-8')
    return None


def check_login_base(query_params: Union[str, dict], debugger: bool = False) -> Optional[dict]:
    global is_user

    if debugger:
        secret = "TcLbyP4sp5eCsowy29YYMgyTNSXbXgPv"
        url = "https://test-unified-auth.shiyuegame.com/service/user/info"
        pid = 164
    else:
        secret = "lBboK4gdDxlKUNnjByIzxVYGYkqojnb9"
        pid = 14
        url = "https://unified-auth.shiyuegame.com/service/user/info"

    token = None
    if isinstance(query_params, str):
        token = query_params
    elif isinstance(query_params, dict) and "token" in query_params:
        token = query_params["token"][0]

    if token:
        info = verify(token, secret)
        if info:
            payload = {
                "token": token,
                "pid": pid
            }
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                info = response.json()
                if info["code"] == 0 and info["message"] == "success":
                    data = info['data']
                    logger.info(f"User: {data['alias']}, ID: {data['username']}, Dept: {data['dept']}")
                    is_user = True
                    return data
                else:
                    logger.error(f"Error: {info}")
            else:
                logger.error(f"Request failed, status code: {response.status_code}")
    return None