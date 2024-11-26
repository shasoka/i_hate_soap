from lxml import etree
from zeep import Client as SOAPClient
from zeep.plugins import HistoryPlugin

from config import MAIN_TNS, WSDL_URL


def gen_auth_header(value: str):
    auth_header = etree.Element("{" + MAIN_TNS + "}AuthHeader")
    auth = etree.SubElement(
        auth_header,
        "{" + MAIN_TNS + "}Authorization",
    )
    auth.text = value
    return auth_header


plugin = HistoryPlugin()
users_client = SOAPClient(
    wsdl=WSDL_URL,
    plugins=[plugin],
)
