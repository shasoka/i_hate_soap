from fastapi import UploadFile
from zeep.exceptions import Fault

from .zeep import client, gen_auth_header


async def upload_file(
    file: UploadFile,
    header: str = "",
):
    try:
        file_content = await file.read()
        with client.settings(raw_response=True):
            response = client.service.upload_file(
                filename=file.filename,
                content=file_content,
                _soapheaders=[gen_auth_header(header)],
            )

        return {
            "status": "Файл успешно отправлен на сервер",
            "server_response": response.content,
        }

    except Fault as e:
        # Обработка ошибок SOAP
        return {"status": "Ошибка", "detail": str(e)}
