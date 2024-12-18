import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Основные пути
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIR = BASE_DIR / "server" / "uploads"

# База данных
DATABASE_URL = os.getenv("DATABASE_URL")

# Параметры JWT
JWT_PRIVATE_KEY = (BASE_DIR / "certs" / "jwt_private.pem").read_text()
JWT_PUBLIC_KEY = (BASE_DIR / "certs" / "jwt_public.pem").read_text()
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 30))

# SOAP
MAIN_TNS = "isd.prac_3"

DEFER_DELAY = 0.1

MAX_ENVELOPE_SIZE = MAX_USER_DIR_SIZE = 100 * 1024 * 1024
MAX_FILE_SIZE = 3 * 1024 * 1024

LOG_LEVEL = 10  # 10 for DEBUG, 50 for CRITICAL

# .SVC
SOAP_SVC_HOST = os.getenv("SOAP_SVC_HOST")
SOAP_SVC_PORT = int(os.getenv("SOAP_SVC_PORT"))
