from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from . import templates

router = APIRouter()


@router.get("/files", response_class=HTMLResponse)
async def show_files(request: Request):
    return templates.TemplateResponse(
        "files.html",
        {"request": request},
    )
