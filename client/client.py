from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from views.files import router as files_router
from views.notif_websocket import router as ws_router
from views.uptime import router as uptime_router
from views.users import router as auth_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(files_router)
app.include_router(ws_router)
app.include_router(uptime_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/files")
