from fastapi import APIRouter, HTTPException
import docker

from ..docker_client import DockerClient

router = APIRouter()
_docker = DockerClient()


@router.get("/containers")
async def list_containers():
    try:
        return await _docker.list_containers()
    except docker.errors.DockerException as exc:
        raise HTTPException(status_code=503, detail=f"Docker daemon unreachable: {exc}")
