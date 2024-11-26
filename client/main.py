import uvicorn

from client import app  # noqa
from config import SOAP_CLNT_HOST, SOAP_CLNT_PORT

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=SOAP_CLNT_HOST,
        port=SOAP_CLNT_PORT,
        reload=True,
        log_level=10,
    )
