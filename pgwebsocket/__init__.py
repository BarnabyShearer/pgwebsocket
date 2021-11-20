"""
Proxy websocket messages to and from PostgreSQL.

Note: This dose not handle authentication and authorization,
ensure you implement them at other layers.
"""

import asyncio
import json
import logging
import traceback
from typing import Any, Awaitable, Callable, Dict, Tuple

import psycopg
from aiohttp import WSMessage, web
from aiohttp.http_websocket import WSMsgType

LOGGER = logging.getLogger(__name__)


Callback = Callable[..., Awaitable[bool]]


async def _pinger(websocket: web.WebSocketResponse) -> None:  # pragma: no cover
    """Loop to ping every 30s to prevent timeouts."""
    while True:
        await asyncio.sleep(30)
        try:
            await websocket.ping()
        except RuntimeError:
            LOGGER.debug("ping error")
            break


class PgWebsocket:  # pragma: no cover
    """An application to handle websocket to Postgresql proxying."""

    _on_msg: Dict[str, Callback] = {}

    def __init__(self, dburl: str, bind: str = "127.0.0.1", port: int = 9000) -> None:
        """Create a websocket server to talk to db."""
        self._dburl = dburl
        self._bind = bind
        self._port = port

    def on_connect(self, callback: Callback) -> None:
        """Register a callback after connection."""
        self._connect = callback

    def on_disconnect(self, callback: Callback) -> None:
        """Register a callback after disconnection."""
        self._disconnect = callback

    def on_msg(self, route: str) -> Callable[[Callback], None]:
        """
        Register a map of callbacks to handle diffrent messages.

        Callbacks can return True to stop processing this message.
        """

        def _wrap(callback: Callback) -> None:
            self._on_msg[route] = callback

        return _wrap

    async def _msg_handler(
        self,
        conn: psycopg.AsyncConnection[Tuple[Any, ...]],
        websocket: web.WebSocketResponse,
        msg_ws: WSMessage,
    ) -> None:
        msg_ws = json.loads(msg_ws.data)
        try:
            if msg_ws[0] in self._on_msg:
                LOGGER.debug("Calling %s(conn, *%s)", msg_ws[0], msg_ws[1:])
                if await self._on_msg[msg_ws[0]](conn, *msg_ws[1:]):
                    return
            async with conn.cursor() as cur:
                await cur.execute(msg_ws[0], msg_ws[1:])
                try:
                    async for record in cur:
                        if record[0] != "":
                            await websocket.send_str(record[0])
                except psycopg.ProgrammingError:
                    pass

        except Exception as err:
            LOGGER.error(traceback.format_exc())
            await websocket.send_str(json.dumps({"error": str(err)}))

    async def _websocket_handler(self, request: web.Request) -> web.WebSocketResponse:
        """Handle incoming websocket connections."""

        LOGGER.info(
            "Websocket connected: %s",
            request.raw_path,
        )

        websocket = web.WebSocketResponse()

        await websocket.prepare(request)
        ping = asyncio.ensure_future(_pinger(websocket))

        async with await psycopg.AsyncConnection.connect(
            self._dburl, autocommit=True
        ) as conn:

            if hasattr(self, "_connect"):
                await self._connect(conn)

            def _notify(msg: psycopg.Notify) -> None:
                LOGGER.debug(msg)
                asyncio.ensure_future(websocket.send_str(msg.payload))

            conn.add_notify_handler(_notify)

            async for msg_ws in websocket:
                LOGGER.debug(msg_ws)
                if msg_ws.type == WSMsgType.CLOSE:
                    LOGGER.debug("Websocket closing")
                    await websocket.close()
                    return websocket
                if msg_ws.type == WSMsgType.ERROR:
                    LOGGER.error(msg_ws)
                    return websocket
                await self._msg_handler(conn, websocket, msg_ws)

        ping.cancel()

        if hasattr(self, "_disconnect"):
            await self._disconnect(conn)

        LOGGER.info(
            "Websocket disconnected: %s",
            request.raw_path,
        )

        return websocket

    def run(self, url: str = r"/") -> None:
        """Start listening for connections."""
        app = web.Application()
        app.router.add_route("GET", url, self._websocket_handler)
        web.run_app(app, host=self._bind, port=self._port)
