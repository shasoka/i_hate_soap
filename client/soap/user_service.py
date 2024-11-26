from lxml.etree import _Element

from .zeep import users_client, plugin


def register_user(
    username: str,
    password: str,
) -> (
    _Element,
    _Element,
    bool,
):
    success: bool = False
    try:
        users_client.service.register(username=username, password=password)
        success: bool = True
    finally:
        request_body = plugin.last_sent["envelope"]
        response_body = plugin.last_received["envelope"]
        return request_body, response_body, success


def login_user(
    username: str,
    password: str,
) -> (
    _Element,
    _Element,
    bool,
):
    success: bool = False
    try:
        users_client.service.login(username=username, password=password)
        success: bool = True
    finally:
        request_body = plugin.last_sent["envelope"]
        response_body = plugin.last_received["envelope"]
        return request_body, response_body, success
