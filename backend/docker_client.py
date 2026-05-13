from typing import Any
import docker
from docker.models.containers import Container
from fastapi.concurrency import run_in_threadpool


class DockerClient:
    def __init__(self):
        self._client = docker.from_env()

    def close(self):
        self._client.close()

    async def list_containers(self) -> list[dict[str, Any]]:
        containers: list[Container] = await run_in_threadpool(
            self._client.containers.list
        )
        return [_normalize_container(c) for c in containers]

    async def inspect_container(self, container_id: str) -> dict[str, Any]:
        raw = await run_in_threadpool(
            self._client.api.inspect_container, container_id
        )
        return raw

    async def get_image_digest(self, image_tag: str) -> str:
        image = await run_in_threadpool(self._client.images.get, image_tag)
        return image.id

    async def stream_logs(self, container_id: str, tail: int = 100):
        """Yield log lines. Caller must run this in a thread via run_in_threadpool
        or iterate from a dedicated thread — docker-py log streaming is synchronous."""
        container: Container = await run_in_threadpool(
            self._client.containers.get, container_id
        )
        return await run_in_threadpool(
            container.logs,
            stream=True,
            follow=True,
            tail=tail,
            timestamps=True,
        )


def _normalize_container(c: Container) -> dict[str, Any]:
    return {
        "id": c.short_id,
        "full_id": c.id,
        "name": c.name,
        "image": c.image.tags[0] if c.image.tags else c.image.short_id,
        "status": c.status,
        "created": c.attrs["Created"],
    }
