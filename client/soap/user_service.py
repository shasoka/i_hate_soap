from lxml.etree import _Element

from .utils import extract_tag_from_xml
from .zeep import default_client, plugin


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
        default_client.service.register(username=username, password=password)
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
        default_client.service.login(username=username, password=password)
        success: bool = True
    finally:
        request_body = plugin.last_sent["envelope"]
        response_body = plugin.last_received["envelope"]
        return request_body, response_body, success


def check_token(token: str) -> bool:
    try:
        default_client.service.check_token(token=token)
    finally:
        return (
            True
            if extract_tag_from_xml(
                plugin.last_received["envelope"],
                "check_tokenResult",
            )
            == "true"
            else False
        )
