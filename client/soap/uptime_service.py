from lxml.etree import _Element

from .zeep import main_client, plugin, gen_auth_header


def get_uptime(header: str) -> (_Element, _Element, bool):
    success: bool = True
    try:
        main_client.service.check_uptime(
            _soapheaders=[gen_auth_header(header)],
        )
        success = True
    finally:
        request_body = plugin.last_sent["envelope"]
        response_body = plugin.last_received["envelope"]
        return request_body, response_body, success
