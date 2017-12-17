import asyncio

import aiohttp
from aiohttp import web
from aiohttp_session import setup as session_setup, get_session
from aiohttp_cas import login_required
from aiohttp_cas import setup as cas_setup
from aiohttp_session.redis_storage import RedisStorage
from aioredis import create_pool
from yarl import URL

CHUNK_SIZE = 10140
BACKEND = URL('http://127.0.0.1:5555')
TIMEOUT = 10


@login_required
async def index(request):
    async with aiohttp.ClientSession() as session:
        session_state = await get_session(request)

        url = request.url.with_host(BACKEND.host).with_port(BACKEND.port).with_scheme(BACKEND.scheme)
        headers = request.headers.copy()
        headers['Host'] = '{}:{}'.format(BACKEND.host, BACKEND.port)
        headers['Remote-User'] = session_state['aiohttp_cas']['username']

        kwargs = dict(
            method=request.method,
            url=url,
            params=getattr(request, 'params', None),
            headers=headers,
            auth=getattr(request, 'auth', None),
            allow_redirects=False,
            encoding=request.charset,
            timeout=TIMEOUT,
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
    app = web.Application()
    pool = await create_pool(('127.0.0.1', 6379), db=0)
    session_setup(app, RedisStorage(pool))
    cas_setup(app, '127.0.0.1:8000', host_prefix='/cas/', version='3', host_scheme='http')
    app.router.add_route('*', '/{tail:.*}', index)
    return app


def main():
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(make_app())
    web.run_app(app)


if __name__ == '__main__':
    main()
