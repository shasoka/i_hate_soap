from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from soap.user_service import login_user, register_user
from soap.utils import element_to_string, extract_tag_from_xml
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
    body, response, success = register_user(username, password)
    formatted_request = element_to_string(body)
    formatted_response = element_to_string(response)

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "soap_body": formatted_request,
            "soap_response": formatted_response,
            "success": success,
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
    body, response, success = login_user(username, password)
    formatted_request = element_to_string(body)
    formatted_response = element_to_string(response)

    access_token: str = ""
    token_type: str = ""

    if success:
        access_token = extract_tag_from_xml(response, "access_token")
        token_type = extract_tag_from_xml(response, "token_type")

    template_response = templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "soap_body": formatted_request,
            "soap_response": formatted_response,
            "success": success,
        },
    )

    if access_token and token_type:
        template_response.set_cookie(key="access_token", value=access_token)
        template_response.set_cookie(key="token_type", value=token_type)

    return template_response
