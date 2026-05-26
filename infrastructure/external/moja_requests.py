import os
import time

import requests

from infrastructure.logger.logger import log, MOJA
from common.constants import constants
from infrastructure.database.models.message import Message
from infrastructure.database.repositories.message_repository import MessageRepository
from infrastructure.database.repositories.setting_repository import SettingRepository
from infrastructure.database.repositories.url_repository import UrlRepository

message_repository = MessageRepository()
setting_repository = SettingRepository()
url_repository = UrlRepository()

def send_get_request(url):
    headers = create_headers()
    if headers is None:
        return None
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        log.error(MOJA, f"{constants.GET_ERROR} {url}: {response.status_code}")
        return None
    return response.json()

def send_post_request(url, data):
    response = requests.post(url, data=data, timeout=10)
    if response.status_code != 200:
        log.error(MOJA, f"{constants.POST_ERROR} {url}: {response.status_code}")
        return None
    return response.json()

def send_post_request_with_headers(url, data):
    headers = create_headers()
    if headers is None:
        return None
    response = requests.post(url, json=data, headers=headers, timeout=10)
    if response.status_code != 200:
        log.error(MOJA, f"{constants.POST_ERROR} {url}: {response.status_code}")
        return None
    return response.json()

def create_headers():
    access_token = get_access_token()
    if access_token is None :
        log.error(MOJA, constants.TOKEN_ERROR)
        message = Message("ERROR", constants.TOKEN_ERROR)
        message_repository.save(message)
        setting_repository.set_auth_error("1")
        return None
    if access_token == "error":
        return None
    return {"Authorization": "Bearer " + access_token}

def get_refresh_token():
    return setting_repository.get_refresh_token()

def is_token_valid():
    expiration = os.environ.get("AccessTokenExpirationTime")
    if expiration is None:
        return False
    return time.time() < float(expiration)

def get_access_token():
    access_token = os.environ.get("AccessToken")
    if access_token is not None and is_token_valid():
        return access_token
    if setting_repository.get_auth_error():
        return "error"
    url = url_repository.get_url_by_label("AccessToken")
    data = {
        "client_id": "moja-site",
        "scope": "openid",
        "refresh_token": get_refresh_token(),
        "grant_type": "refresh_token"
    }
    response = send_post_request(url, data)
    if response is None:
        log.error(MOJA, constants.TOKEN_ERROR)
        return None
    access_token = response["access_token"]
    expiration_time = response["expires_in"] - 30
    os.environ["AccessToken"] = access_token
    os.environ["AccessTokenExpirationTime"] = str(time.time() + expiration_time)
    return access_token
