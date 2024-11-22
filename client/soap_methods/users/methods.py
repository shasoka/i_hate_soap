import requests
from requests import Response

from soap_methods.users.xmls import LOGIN_BODY

SOAP_URL = "http://localhost:8000/"


def register_user(username: str, password: str) -> Response:
    """Отправка SOAP-запроса для регистрации пользователя"""
    soap_body = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="isd.prac_3">
        <soapenv:Header/>
        <soapenv:Body>
            <tns:register>
                <tns:username>{username}</tns:username>
                <tns:password>{password}</tns:password>
            </tns:register>
        </soapenv:Body>
    </soapenv:Envelope>
    """
    headers: dict = {"Content-Type": "text/xml"}
    response: Response = requests.post(
        SOAP_URL,
        data=soap_body,
        headers=headers,
    )
    return response


def login_user(username: str, password: str) -> Response:
    """
    Функция для отправки SOAP-запроса для логина пользователя.

    :param username: Имя пользователя.
    :param password: Пароль пользователя.
    :return: Объект Response с содержимым SOAP-ответа.
    """

    soap_body: str = LOGIN_BODY % (username, password)
    headers: dict = {"Content-Type": "text/xml"}
    response: Response = requests.post(
        SOAP_URL,
        data=soap_body,
        headers=headers,
    )
    return response
