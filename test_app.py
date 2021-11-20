#!/usr/bin/env python3
"""
Minimal Example.

$ docker compose up -d
$ npm install -g wscat
$ wscat --connect localhost:9000/
> ["pg_notify", "clients", "hi"]
< hi
> ["test", "hi"]
"""

import logging

from pgwebsocket import Ctx, PgWebsocket

logging.basicConfig(level=logging.DEBUG)
app = PgWebsocket("", "0.0.0.0")


@app.on_connect
async def _on_connect(ctx: Ctx) -> bool:
    await ctx.execute("LISTEN clients;")
    return False


@app.on_msg("test")
async def _test(ctx: Ctx, arg: str) -> bool:
    return True


def main() -> None:
    """Entrypoint."""
    app.run()


if __name__ == "__main__":
    main()
