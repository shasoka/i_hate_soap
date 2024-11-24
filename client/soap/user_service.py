from lxml.etree import _Element

from .utils import extract_tag_from_xml
from .zeep import client, plugin


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
        client.service.register(username=username, password=password)
        success: bool = True
    finally:
        request_body = plugin.last_request
        response_body = plugin.last_response
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
        client.service.login(username=username, password=password)
        success: bool = True
    finally:
        request_body = plugin.last_request
        response_body = plugin.last_response
        return request_body, response_body, success


def check_token(token: str) -> bool:
    try:
        client.service.check_token(token=token)
    finally:
        return (
            True
            if extract_tag_from_xml(
                plugin.last_response,
                "check_tokenResult",
            )
            == "true"
            else False
        )
