import asyncio
from typing import Any

from fastapi import WebSocket

from .docker_client import DockerClient

_QUEUE_MAX = 500


class WSManager:
    def __init__(self, docker_client: DockerClient):
        self._docker = docker_client
        # container_id → set of active WebSocket connections
        self._subscribers: dict[str, set[WebSocket]] = {}
        # container_id → background streaming task
        self._stream_tasks: dict[str, asyncio.Task] = {}

    async def connect(self, container_id: str, ws: WebSocket):
        await ws.accept()
        if container_id not in self._subscribers:
            self._subscribers[container_id] = set()
        self._subscribers[container_id].add(ws)

        if container_id not in self._stream_tasks:
            task = asyncio.create_task(self._stream_container(container_id))
            self._stream_tasks[container_id] = task

    def disconnect(self, container_id: str, ws: WebSocket):
        subs = self._subscribers.get(container_id, set())
        subs.discard(ws)
        if not subs:
            self._subscribers.pop(container_id, None)
            task = self._stream_tasks.pop(container_id, None)
            if task:
                task.cancel()

    async def _stream_container(self, container_id: str):
        try:
            log_iter = await self._docker.stream_logs(container_id, tail=100)
            await asyncio.to_thread(self._blocking_stream, container_id, log_iter)
        except Exception as exc:
            await self._broadcast(container_id, {
                "type": "error",
                "container_id": container_id,
                "message": str(exc),
            })

    def _blocking_stream(self, container_id: str, log_iter):
        """Runs in a thread — docker-py log iteration is synchronous."""
        loop = asyncio.get_event_loop()
        for chunk in log_iter:
            line = chunk.decode("utf-8", errors="replace").rstrip()
            msg: dict[str, Any] = {
                "type": "log",
                "container_id": container_id,
                "line": line,
            }
            asyncio.run_coroutine_threadsafe(
                self._broadcast(container_id, msg), loop
            ).result()

        asyncio.run_coroutine_threadsafe(
            self._broadcast(container_id, {
                "type": "error",
                "container_id": container_id,
                "message": "container stopped",
            }), loop
        ).result()

    async def _broadcast(self, container_id: str, message: dict[str, Any]):
        dead: set[WebSocket] = set()
        for ws in list(self._subscribers.get(container_id, set())):
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.disconnect(container_id, ws)
