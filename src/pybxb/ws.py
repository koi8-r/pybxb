import types
import json
from pprint import pprint as pp
from urllib.parse import parse_qsl
from aiohttp import web
from multidict import MultiDict, MultiDictProxy
from aiohttp.web import Request, Response


assert type(pp) is type(lambda _: _)


def route(this, verb='GET', path='/'):
    def decorator(fn):
        def w(req: Request) -> Response:
            assert req.__class__ is Request
            bxb_version = req.headers.get('X-BXB-Version') or 'null'
            charset = req.charset or 'utf-8'
            content_type = req.content_type or 'application/octet-stream'
            try:
                r = fn(req)
            except Exception as ex:
                raise ex
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
    if req.content_type == 'application/x-www-form-urlencoded':
        charset = req.charset or 'utf-8'
        out = MultiDict(req.query)

        bytes_body = await req.read()
        if bytes_body:
            out.extend(parse_qsl(bytes_body.rstrip().decode(charset),
                                 keep_blank_values=True,
                                 encoding=charset))

        # Make immutable dict with auth[param] keys like auth_param
        res = MultiDictProxy(MultiDict((
                  k.startswith('auth[') and k.endswith(']') and
                  'auth_' + k[5:-1]
                  or k,
                  v,) for k, v in out.items()))

        print('\n'.join('{}: {}'.format(k, v) for k, v in res.items()))

    return Response(status=200, text='OK')


httpd.run()
