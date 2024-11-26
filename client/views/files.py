import base64
import os
import tempfile

from fastapi import APIRouter, Request, UploadFile, WebSocket, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from starlette.responses import RedirectResponse

from soap.file_service import upload_file, get_last, get_csv
from soap.utils import (
    element_to_string,
    extract_tag_from_str,
    extract_tag_from_xml,
)
from websocket.manager import connection_manager
from . import templates

router = APIRouter()


@router.get("/files", response_class=HTMLResponse)
async def show_files(request: Request):
    if request.cookies.get("access_token") is not None:
        return templates.TemplateResponse(
            "files.html",
            {
                "request": request,
                "authenticated": True,
            },
        )
    else:
        return RedirectResponse(url="/login")


@router.post("/files")
def post_file(file: UploadFile, request: Request):
    body, response, success = upload_file(
        file=file,
        header=str(request.cookies.get("token_type"))
        + " "
        + str(request.cookies.get("access_token")),
    )

    formatted_request = element_to_string(body)
    formatted_response = element_to_string(response)

    # Получаем url для просмотра статуса загрузки
    upload_url: str = (
        extract_tag_from_str(
            formatted_response,
            "upload_fileResult",
        )[-42:-1]
        if success
        else None
    )

    return templates.TemplateResponse(
        "files.html",
        {
            "request": request,
            "soap_body": formatted_request,
            "soap_response": formatted_response,
            "upload_url": upload_url,
            "success": success,
        },
    )


@router.get("/upload/{uid}")
def get_upload(uid: str, request: Request):
    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "uid": uid,
        },
    )


@router.post("/upload/{uid}")
async def post_upload(uid: str, callback_data: dict):
    ws: WebSocket = connection_manager.active_connections.get(uid)
    if ws:
        await ws.send_json(callback_data)
        return {"status": "updated"}

    raise HTTPException(status_code=404, detail="Not found")


@router.get("/last_upload")
def get_last_upload(request: Request):
    body, response, success = get_last(
        header=str(request.cookies.get("token_type"))
        + " "
        + str(request.cookies.get("access_token")),
    )

    formatted_request = element_to_string(body)
    formatted_response = element_to_string(response)

    return templates.TemplateResponse(
        "last_upload.html",
        {
            "request": request,
            "soap_body": formatted_request,
            "soap_response": formatted_response,
            "success": success,
        },
    )


@router.get("/csv")
def get_files_csv(request: Request):
    body, response, success = get_csv(
        header=str(request.cookies.get("token_type"))
        + " "
        + str(request.cookies.get("access_token"))
    )

    formatted_request = element_to_string(body)
    formatted_response = element_to_string(response)

    if success:
        fname: str = extract_tag_from_xml(response, "name")
        mime: str = extract_tag_from_xml(response, "type")
        fcontent: bytes = base64.b64decode(
            extract_tag_from_xml(
                response,
                "data",
            )
        )

        # Сохранение во временный файл
        with tempfile.NamedTemporaryFile(
            delete=False,
            mode="wb",
        ) as tmp_file:
            tmp_file.write(fcontent)
            tmp_file = tmp_file.name

        return templates.TemplateResponse(
            "csv.html",
            {
                "request": request,
                "soap_body": formatted_request,
                "soap_response": formatted_response,
                "success": success,
                "download_link": f"/download"
                f"?tmp_file={os.path.basename(tmp_file)}"
                f"&original_fname={fname}"
                f"&mime={mime}",
            },
        )


@router.get("/download")
def download_file(
    tmp_file: str,
    original_fname: str,
    mime: str,
):
    file_path = os.path.join(tempfile.gettempdir(), tmp_file)
    return FileResponse(
        file_path,
        media_type=mime,
        filename=original_fname,
    )
