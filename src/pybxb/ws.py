import types
import json
from pprint import pprint as pp
from aiohttp import web
from aiohttp.web import Request, Response


assert type(pp) is type(lambda _: _)


def route(this, verb='GET', path='/'):
    def decorator(fn):
        def w(req: Request) -> Response:
            assert req.__class__ is Request
            bxb_version = req.headers.get('X-BXB-Version') or 'null'
            encoding = req.charset or 'utf-8'
            content_type = req.content_type

            r = fn(req)
            return r
        this.router.add_route(verb, path, w)
        return w
    return decorator


httpd = web.Application()
httpd.route = types.MethodType(route, httpd)
httpd.run = types.MethodType(lambda this: web.run_app(this), httpd)
httpd.MAX_UPLOAD_SIZE = 1024  # 1024**2 = 1M


@httpd.route(path='/')
async def index(req: Request):
    return Response(status=200, text='index', content_type='text/plain')


@httpd.route(verb='POST', path='/')
async def io(req: Request):
    # bytes_body = await req.read()
    print(await req.post())
    print(req.query)

    return Response(status=200, text='OK')


httpd.run()
