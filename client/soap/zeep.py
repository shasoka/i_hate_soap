from lxml import etree
from zeep import Client as SOAPClient
from zeep.plugins import HistoryPlugin


def gen_auth_header(value: str):
    auth_header = etree.Element("{isd.prac_3}AuthHeader")
    auth = etree.SubElement(
        auth_header,
        "{isd.prac_3}Authorization",
    )
    auth.text = value
    return auth_header


plugin = HistoryPlugin()
wsdl = "http://localhost:8000/?wsdl"
default_client = SOAPClient(
    wsdl=wsdl,
    plugins=[plugin],
)
