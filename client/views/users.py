from xml.dom.minidom import parseString

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from soap_methods.users.methods import register_user, login_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse)
async def show_register(request: Request):
    """Страница регистрации"""
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    """Обработка регистрации"""
    response = register_user(username, password)
    if response.status_code == 200:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "message": "Registration successful!"},
        )
    return templates.TemplateResponse(
        "register.html", {"request": request, "error": "Registration failed!"}
    )


@router.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    """Страница логина"""
    return templates.TemplateResponse("login.html", {"request": request})


def format_xml(xml_string: str) -> str:
    """Форматирует XML строку с добавлением переносов и отступов."""
    try:
        dom = parseString(xml_string)
        return dom.toprettyxml()
    except Exception:
        return (
            xml_string  # Возврат без изменений, если форматирование не удалось
        )


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    """Обработка логина"""
    response = login_user(username, password)
    formatted_response = format_xml(response.content.decode("utf-8"))
    if response.status_code == 200:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "soap_response": formatted_response,
                "success": True,
            },
        )
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "soap_response": formatted_response,
            "success": False,
        },
    )
