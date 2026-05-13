from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .docker_client import DockerClient
from .scanner import Scanner
from .ws_manager import WSManager
from .api import containers, scan, logs


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.docker = DockerClient()
    app.state.scanner = Scanner(app.state.docker)
    app.state.ws_manager = WSManager(app.state.docker)
    asyncio.create_task(app.state.scanner.update_trivy_db())
    yield
    app.state.docker.close()


app = FastAPI(title="Docker Doctor", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(containers.router, prefix="/api")
app.include_router(scan.router, prefix="/api")
app.include_router(logs.router)

try:
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
except RuntimeError:
    pass
