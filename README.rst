Python CAS Gateway
==================

This is a HTTP CAS gateway built upon ``aiohttp`` and ``aiohttp-cas``. Redis is used for
session storage.

You should not expose this gateway directly to the internet. Rather it is expected that
it will sit between your reverse proxy and your application.

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
      --require-attribute REQUIRE_ATTRIBUTE
                            Require the given CAS attribute to be present and not
                            set to an empty string. Requires CAS version 3.
                            (default: None)

    required named arguments:
      --backend-url BACKEND_URL
                            URL to the backend to be proxied (e.g.
                            http://myhost.com:8888) (default: None)
      --cas-url CAS_URL     URL to the CAS server (default: None)

S3 Support (experimental)
-------------------------

Backend URLs can also reference Amazon S3 buckets. For example:

.. code-block:: bash

    cas_gateway --backend-url s3://my-bucket --cas-url http://cas.example.com/

The `index.html` suffix will be appended to bucket keys where needed.

Docker
------

.. code-block:: bash

    docker build . -t python-cas-gateway
    docker run python-cas-gateway

Updating docker hub
-------------------

.. code-block:: bash

    # Update the Pipfile (if requirements in setup.py have changed)
    pipenv install -e .

    # Build image
    docker build -t adamcharnock/python-cas-gateway .

    # Login to docker hub
    docker login

    # Push to registry
    docker push adamcharnock/python-cas-gateway
