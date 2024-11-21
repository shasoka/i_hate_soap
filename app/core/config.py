import os
from pathlib import Path

from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Основные пути
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# База данных
DATABASE_URL = os.getenv("DATABASE_URL")

# Параметры JWT
JWT_PRIVATE_KEY = (BASE_DIR / "certs" / "jwt_private.pem").read_text()
JWT_PUBLIC_KEY = (BASE_DIR / "certs" / "jwt_public.pem").read_text()
JWT_ALGORITHM = "RS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 30))
