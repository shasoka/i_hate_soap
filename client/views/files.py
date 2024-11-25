from fastapi import APIRouter, Request, UploadFile
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

from soap.file_service import upload_file
from soap.utils import element_to_string
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

    return templates.TemplateResponse(
        "files.html",
        {
            "request": request,
            "soap_body": formatted_request,
            "soap_response": formatted_response,
            "success": success,
        },
    )
