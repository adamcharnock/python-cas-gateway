Python CAS Gateway
==================

This is a HTTP CAS gateway built upon ``aiohttp`` and ``aiohttp-cas``. Redis is used for
session storage.

You should not expose this gateway directly to the internet. Rather it is expected that
it will sit between your reverse proxy and your software.

This is a proof of concept and the proxying logic is naive.

Use
---

.. code-block:: plain

    $ cas_gateway -h
    usage: cas_gateway [-h] [--redis-url REDIS_URL] [--timeout TIMEOUT]
                       [--bind-host BIND_HOST] [--bind-port BIND_PORT]
                       [--cas-version CAS_VERSION] [--chunk-size CHUNK_SIZE]
                       --backend-url BACKEND_URL --cas-url CAS_URL

    Python CAS Gateway

    optional arguments:
      -h, --help            show this help message and exit
      --redis-url REDIS_URL
                            Redis URL (default: redis://127.0.0.1:6379/0)
      --timeout TIMEOUT     Request timeout (default: 10)
      --bind-host BIND_HOST
                            Address to bind to (default: 0.0.0.0)
      --bind-port BIND_PORT
                            Port to bind to (default: 8000)
      --cas-version CAS_VERSION
                            CAS version in use (default: 3)
      --chunk-size CHUNK_SIZE
                            Chunk size for streaming responses back to the client
                            (default: 4096)

    required named arguments:
      --backend-url BACKEND_URL
                            URL to the backend to be proxied (e.g.
                            http://myhost.com:8888) (default: None)
      --cas-url CAS_URL     URL to the CAS server (default: None)


Docker
------

    docker build . -t python-cas-gateway
    docker run python-cas-gateway

