from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from soap_methods import format_xml, extract_token_from_xml
from soap_methods.users.methods import login_user, register_user
from . import templates

router = APIRouter()


@router.get("/register", response_class=HTMLResponse)
async def show_register(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request},
    )


@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    body, response = register_user(username, password)
    formatted_response = format_xml(response.content.decode("utf-8"))
    if response.status_code == 200:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "soap_body": body,
                "soap_response": formatted_response,
                "success": True,
            },
        )
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "soap_body": body,
            "soap_response": formatted_response,
            "success": False,
        },
    )


@router.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request},
    )


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    body, response = login_user(username, password)
    formatted_response = format_xml(response.content.decode("utf-8"))

    access_token = extract_token_from_xml(
        response.content.decode("utf-8"),
        "access_token",
    )
    token_type = extract_token_from_xml(
        response.content.decode("utf-8"),
        "token_type",
    )

    if response.status_code == 200:
        # Успешный логин
        template_response = templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "soap_body": body,
                "soap_response": formatted_response,
                "success": True,
            },
        )
        template_response.set_cookie(key="access_token", value=access_token)
        template_response.set_cookie(key="token_type", value=token_type)
        return template_response

    return templates.TemplateResponse(
        # Неудачный логин
        "login.html",
        {
            "request": request,
            "soap_body": body,
            "soap_response": formatted_response,
            "success": False,
        },
    )
