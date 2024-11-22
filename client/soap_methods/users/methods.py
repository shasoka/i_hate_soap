import requests
from requests import Response

from soap_methods.users.xmls import LOGIN_BODY, REGISTER_BODY

SOAP_URL = "http://localhost:8000/"


def register_user(username: str, password: str) -> (str, Response):
    soap_body = REGISTER_BODY % (username, password)
    headers: dict = {"Content-Type": "text/xml"}
    response: Response = requests.post(
        SOAP_URL,
        data=soap_body,
        headers=headers,
    )
    return soap_body, response


def login_user(username: str, password: str) -> (str, Response):
    soap_body: str = LOGIN_BODY % (username, password)
    headers: dict = {"Content-Type": "text/xml"}
    response: Response = requests.post(
        SOAP_URL,
        data=soap_body,
        headers=headers,
    )
    return soap_body, response
