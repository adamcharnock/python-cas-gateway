import argparse
import asyncio
import logging

import aiohttp
from aiohttp import web
from aiohttp.web_response import Response
from aiohttp_session import setup as session_setup, get_session
from aiohttp_cas import login_required
from aiohttp_cas import setup as cas_setup
from aiohttp_session.redis_storage import RedisStorage
from aiohttp_remotes import setup as remotes_setup, XForwardedRelaxed
from aioredis import create_pool
from yarl import URL

CHUNK_SIZE = 10140


async def ready_check(request):
    return Response(content_type='text/plain')


@login_required
async def handle(request):
    async with aiohttp.ClientSession() as session:
        session_state = await get_session(request)
        backend_url = request.app.settings.backend_url

        url = request.url.with_host(backend_url.host).with_port(backend_url.port).with_scheme(backend_url.scheme)
        headers = request.headers.copy()
        headers['Host'] = '{}:{}'.format(backend_url.host, backend_url.port)
        headers['Remote-User'] = session_state['aiohttp_cas']['username']

        kwargs = dict(
            method=request.method,
            url=url,
            params=getattr(request, 'params', None),
            headers=headers,
            auth=getattr(request, 'auth', None),
            allow_redirects=False,
            encoding=request.charset,
            timeout=request.app.settings.timeout,
        )

        async with session.request(**kwargs) as remote_response:
            print("{} {} -> {}".format(request.method, url, remote_response.status))
            response = web.StreamResponse(
                status=remote_response.status,
                reason=remote_response.reason,
                headers=remote_response.headers
            )
            await response.prepare(request)

            while True:
                chunk = await remote_response.content.read(CHUNK_SIZE)
                if not chunk:
                    break
                response.write(chunk)
            print("Done")
        return response


async def make_app():
    parser = argparse.ArgumentParser(
        description='Python CAS Gateway',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--redis-url', help='Redis URL', default='redis://127.0.0.1:6379/0')
    parser.add_argument('--timeout', type=int, help='Request timeout', default=10)
    parser.add_argument('--bind-host', help='Address to bind to', default='0.0.0.0')
    parser.add_argument('--bind-port', type=int, help='Port to bind to', default='8000')
    parser.add_argument('--cas-version', type=int, help='CAS version in use', default=3)
    parser.add_argument('--chunk-size', type=int, help='Chunk size for streaming responses back to the client',
                        default=1024*4)

    required_named = parser.add_argument_group('required named arguments')
    required_named.add_argument('--backend-url', help='URL to the backend to be proxied (e.g. http://myhost.com:8888)',
                                required=True)
    required_named.add_argument('--cas-url', help='URL to the CAS server', required=True)

    args = parser.parse_args()
    app = web.Application()

    print("Configuring...")

    app.settings = type('Settings', (object,), dict(
        backend_url=URL(args.backend_url),
        cas_url=URL(args.cas_url),
        redis_url=URL(args.redis_url),
        timeout=args.timeout,
        bind_host=args.bind_host,
        bind_port=args.bind_port,
        # aiohttp_cas was this as a string
        cas_version=str(args.cas_version),
    ))()

    print("Connecting to redis...")
    pool = await create_pool(
        (app.settings.redis_url.host or '127.0.0.1', app.settings.redis_url.port or 6379),
        db=int(app.settings.redis_url.path.strip('/') or 0),
        create_connection_timeout=10,
        password=app.settings.redis_url.password,
    )

    await remotes_setup(app, XForwardedRelaxed())
    session_setup(app, RedisStorage(pool))

    u = app.settings.cas_url
    cas_setup(
        app=app,
        host='{}:{}'.format(u.host, u.port) if u.port != 80 else u.host,
        host_prefix=app.settings.cas_url.path,
        version=app.settings.cas_version,
        host_scheme=app.settings.cas_url.scheme
    )
    app.router.add_route('GET', '/cas-gateway-ready', ready_check)
    app.router.add_route('*', '/{tail:.*}', handle)

    return app


def main():
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(make_app())
    web.run_app(app, host=app.settings.bind_host, port=app.settings.bind_port)


if __name__ == '__main__':
    main()
