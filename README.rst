Python CAS Gateway
==================

This is a HTTP CAS gateway built upon ``aiohttp`` and ``aiohttp-cas``. Redis is used for
session storage.

You should not expose this gateway directly to the internet. Rather it is expected that
it will sit between your reverse proxy and your software.

This is a proof of concept and the proxying logic is naive.

Docker
------

    docker build . -t python-cas-gateway
    docker run python-cas-gateway

