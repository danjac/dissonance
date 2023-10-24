import json
from collections.abc import AsyncGenerator

import psycopg
from django.db import connection
from django.http import StreamingHttpResponse


def notify(listen_to: str, event: str, data: str = "none") -> None:
    with connection.cursor() as cursor:
        payload = json.dumps(
            {
                "event": event,
                "data": data,
            },
        )
        cursor.execute(f"NOTIFY {listen_to}, '{payload}'")


async def event_stream(listen_to: str) -> StreamingHttpResponse:
    connection_params = connection.get_connection_params()
    connection_params.pop("cursor_factory")

    conn = await psycopg.AsyncConnection.connect(
        **connection_params,
        autocommit=True,
    )

    async def _event_stream() -> AsyncGenerator[str, None]:
        async with conn.cursor() as cursor:
            await cursor.execute(f"LISTEN {listen_to}")
            async for event in conn.notifies():
                payload = json.loads(event.payload)
                yield f"event: {payload['event']}\ndata: {payload['data']}\n\n"

    return StreamingHttpResponse(
        streaming_content=_event_stream(),
        content_type="text/event-stream",
    )
