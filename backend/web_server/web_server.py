import functools
import ssl
import json

from aiohttp import web

from common import initLogger
logger = initLogger('WebServer')


OK_STATUS = 'OK'


def respond_ok(response=None, text=None):
    logger.info(f'responding ok {response} {text}')

    if response is not None:
        text = json.dumps(response)
    return web.Response(content_type='text/json', text=text, status=200)


def respond_error(response=None, text=None):
    logger.info(f'responding error {response} {text}')

    if response is not None:
        text = json.dumps(response)
    return web.Response(content_type='text/json', text=text, status=400)


def respond_failure(response=None, text=None):
    logger.error(f'responding failure {response} {text}')
    if response is not None:
        text = json.dumps(response)
    return web.Response(content_type='text/json', text=text, status=500)


class WebServer:
    def __init__(self, handler, host=None, port=None, ssl_files=None):
        self._handler = handler
        self._host = host
        self._port = port
        self._get_prefix = 'get_'
        self._post_prefix = 'post_'
        self._ssl_files = ssl_files
        self._app = None

    def run(self):
        ssl_context = None
        if self._ssl_files is not None:
            if not isinstance(self._ssl_files, tuple):
                raise TypeError('Expected ssl_files argument as tuple')

            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(certfile=self._ssl_files[0], keyfile=self._ssl_files[1])

        self._app = web.Application()
        self._register_handlers()
        web.run_app(app=self._app, host=self._host, port=self._port, ssl_context=ssl_context)

    def _register_handlers(self):
        home_handler = getattr(self._handler, 'get_home', None)
        if home_handler is None:
            raise NotImplementedError('Given request handler has not implemented handle_home() method')
        self._app.router.add_get('/', functools.partial(self._handle_wrapper, home_handler))
        logger.info(f'Registered web resource for GET: /')

        for attr in dir(self._handler):
            if attr.startswith(self._get_prefix):
                method_name = attr[len(self._get_prefix):]
                method = getattr(self._handler, attr)
                self._app.router.add_get(f'/{method_name}',
                                         functools.partial(self._handle_wrapper, method))
                logger.info(f'Registered web resource for GET: /{method_name}')

            elif attr.startswith(self._post_prefix):
                method_name = attr[len(self._post_prefix):]
                method = getattr(self._handler, attr)
                self._app.router.add_post(f'/{method_name}',
                                          functools.partial(self._handle_wrapper, method))
                logger.info(f'Registered web resource for POST: /{method_name}')

    async def _handle_wrapper(self, handler, request: web.Request):
        args = dict(zip(request.query.keys(), request.query.values()))
        try:
            result = await handler(args)
        except AttributeError as e:
            return respond_error(response={
                'error': str(e), 'error_type': 'bad arguments'
            })
        except RuntimeError as e:
            return respond_error(response={
                'error': str(e), 'error_type': 'negative response'
            })
        except Exception as e:
            return respond_failure(response={
                'error': str(e), 'error_type': 'server failure'
            })

        return respond_ok(response={'result': result})
