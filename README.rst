===========
pgwebsocket
===========
.. image:: https://readthedocs.org/projects/pgwebsocket/badge/?version=latest
    :target: https://pgwebsocket.readthedocs.io/en/latest/
.. image:: https://img.shields.io/pypi/v/pgwebsocket?color=success
    :target: https://pypi.org/project/pgwebsocket

Async websocket to PostgreSQL proxy.

Install
-------

.. code-block:: bash

    python3 -m pip install pgwebsocket

Usage
-----

.. code-block:: python

    from pgwebsocket import PgWebsocket
    
    app = PgWebsocket("")
    
    @app.on_connect
    async def _on_connect(ctx):
        await ctx.execute("LISTEN clients;")
    
    @app.on_disconnect
    async def _on_disconnect(ctx):
        await ctx.execute("UNLISTEN clients;")
    
    if __name__ == '__main__':
        app.run()


