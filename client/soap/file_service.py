from io import BytesIO

from fastapi import UploadFile
from lxml.etree import _Element
from pymtom_xop import MtomAttachment, MtomTransport
from requests import Response
from zeep import Client

from .utils import fastapi_file_type_to_bytesio
from .zeep import gen_auth_header, plugin


def upload_file(
    file: UploadFile,
    header: str = "",
) -> (
    _Element,
    _Element,
    bool,
):
    # Создание MTOM-вложения
    bytes_io: BytesIO = fastapi_file_type_to_bytesio(file)
    attachment = MtomAttachment(bytes_io, file.filename)
    mtom_transport = MtomTransport()
    mtom_transport.add_files(files=[attachment])
    bytes_io.close()

    # Создание MTOM-клиента
    mtom_client = Client(
        wsdl="http://localhost:8000/?wsdl",
        transport=mtom_transport,
        plugins=[plugin],
    )

    with mtom_client.settings(raw_response=True):
        response: Response = mtom_client.service.upload_file(
            filename=file.filename,
            content=attachment.get_cid(),
            _soapheaders=[gen_auth_header(header)],
        )

    success: bool = True if response.status_code == 200 else False

    request_body = plugin.last_sent["envelope"]
    response_body = response.content.decode("utf-8")
    return request_body, response_body, success
