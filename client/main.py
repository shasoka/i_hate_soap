import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from views.files import router as files_router
from views.users import router as auth_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(files_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/files")


if __name__ == "__main__":
    uvicorn.run(
        app,
        port=7999,  # Клиент работает на порту 7999, сервер на 8000
    )
