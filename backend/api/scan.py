from fastapi import APIRouter, HTTPException
import docker

from ..scanner import Scanner
from ..docker_client import DockerClient

router = APIRouter()
_scanner = Scanner(DockerClient())


@router.post("/scan/{container_id}")
async def scan_container(container_id: str):
    try:
        return await _scanner.scan_container(container_id)
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail=f"Container {container_id} not found")
    except docker.errors.DockerException as exc:
        raise HTTPException(status_code=503, detail=f"Docker error: {exc}")
