===========
pgwebsocket
===========
.. image:: https://readthedocs.org/projects/pgwebsocket/badge/?version=latest
    :target: https://pgwebsocket.readthedocs.io/en/latest/?badge=latest

.. image:: https://badge.fury.io/py/pgwebsocket.svg
    :target: https://badge.fury.io/py/pgwebsocket

Async websocket to PostgreSQL proxy.

Install
-------

::

    python3 -m pip install pgwebsocket

Usage
-----

::

    from pgwebsocket import PgWebsocket
    
    app = PgWebsocket(
        "postgresql://"
    )
    
    @app.on_connect
    async def on_connect(ctx):
        """"""
        ctx.subscribed = []
        await ctx.execute("LISTEN all;")
    
    @app.on_disconnect
    async def on_disconnect(ctx):
        """"""
        await ctx.execute("UNLISTEN all;")
    
    if __name__ == '__main__':
        app.run()


