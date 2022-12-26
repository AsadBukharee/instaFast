from fastapi import FastAPI
from routes import insta_route, auth_route, route_login, route_users
from models import insta
from starlette.middleware.cors import CORSMiddleware
from database import engine
from fastapi.staticfiles import StaticFiles

origins = [
    "http://localhost",
    "http://localhost:8000"
    "http://localhost:8080",
]

insta.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(auth_route.router, prefix="")
app.include_router(insta_route.router, prefix="/ig")
app.include_router(route_login.router, prefix="/login")
app.include_router(route_users.router, prefix="/user")