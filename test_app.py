#!/usr/bin/env python3
"""
Minimal Example.

$ docker compose up -d
$ npm install -g wscat
$ wscat --connect localhost:9000/
> ["SELECT pg_notify(%s, %s);", "clients", "hi"]
< hi
> ["test", "hi"]
"""

import logging
from typing import Any, Tuple

from psycopg import AsyncConnection

from pgwebsocket import PgWebsocket

logging.basicConfig(level=logging.DEBUG)
app = PgWebsocket("", "0.0.0.0")


@app.on_connect
async def _on_connect(conn: AsyncConnection[Tuple[Any, ...]]) -> bool:
    print("Connect", conn)
    await conn.execute("LISTEN clients;")
    return False


@app.on_msg("test")
async def _test(conn: AsyncConnection[Tuple[Any, ...]], arg: str) -> bool:
    return True


def main() -> None:
    """Entrypoint."""
    app.run()


if __name__ == "__main__":
    main()
