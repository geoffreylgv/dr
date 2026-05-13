from fastapi import APIRouter, HTTPException, Request
import docker

router = APIRouter()


@router.post("/scan/{container_id}")
async def scan_container(container_id: str, request: Request):
    try:
        return await request.app.state.scanner.scan_container(container_id)
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail=f"Container {container_id} not found")
    except docker.errors.DockerException as exc:
        raise HTTPException(status_code=503, detail=f"Docker error: {exc}")
