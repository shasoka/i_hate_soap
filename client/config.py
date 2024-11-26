import os

from dotenv import load_dotenv

load_dotenv()


# SOAP Server
WSDL_URL: str = "http://localhost:8000/?wsdl"
MAIN_TNS: str = "isd.prac_3"

# SOAP Client
SOAP_CLNT_HOST: str = os.getenv("SOAP_CLNT_HOST")
SOAP_CLNT_PORT: int = int(os.getenv("SOAP_CLNT_PORT"))
