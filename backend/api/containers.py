from fastapi import APIRouter, HTTPException, Request
import docker

router = APIRouter()


@router.get("/containers")
async def list_containers(request: Request):
    try:
        return await request.app.state.docker.list_containers()
    except docker.errors.DockerException as exc:
        raise HTTPException(status_code=503, detail=f"Docker daemon unreachable: {exc}")


@router.get("/health")
async def health(request: Request):
    try:
        containers = await request.app.state.docker.list_containers()
        return {"status": "ok", "containers": len(containers)}
    except docker.errors.DockerException as exc:
        raise HTTPException(status_code=503, detail=f"Docker daemon unreachable: {exc}")
