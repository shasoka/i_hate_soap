from fastapi import APIRouter, Request

from soap.uptime_service import get_uptime
from soap.utils import (
    element_to_string,
)
from . import templates

router = APIRouter()


@router.get("/uptime")
def get_uptime_stats(request: Request):
    body, response, success = get_uptime(
        header=str(request.cookies.get("token_type"))
        + " "
        + str(request.cookies.get("access_token"))
    )

    formatted_request = element_to_string(body)
    formatted_response = element_to_string(response)

    return templates.TemplateResponse(
        "uptime.html",
        {
            "request": request,
            "soap_body": formatted_request,
            "soap_response": formatted_response,
            "success": success,
        },
    )
