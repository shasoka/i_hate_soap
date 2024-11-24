from fastapi import APIRouter, Request, UploadFile
from fastapi.responses import HTMLResponse

from soap.file_service import upload_file
from soap.user_service import check_token
from . import templates

router = APIRouter()


@router.get("/files", response_class=HTMLResponse)
async def show_files(request: Request):
    if not (
        access_token := request.cookies.get("access_token")
    ) or not check_token(access_token):
        return templates.TemplateResponse(
            "files.html",
            {
                "request": request,
                "authenticated": False,
            },
        )

    return templates.TemplateResponse(
        "files.html",
        {
            "request": request,
            "authenticated": True,
        },
    )


@router.post("/upload")
async def post_file(file: UploadFile, request: Request):
    return await upload_file(
        file=file,
        header=request.cookies.get("token_type")
        + " "
        + request.cookies.get("access_token"),
    )
