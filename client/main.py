from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from views.users import router as auth_router

app = FastAPI()

app.include_router(auth_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=7999)
