import functools
import ssl
import logging

from aiohttp import web

from .request_handler import RequestHandler


class WebServer:
    def __init__(self, handler: RequestHandler, host=None, port=None, ssl_cafile=None):
        self._handler = handler
        self._host = host
        self._port = port
        self._get_prefix = 'handle_'
        self._post_prefix = 'post_'
        self._ssl_cafile = ssl_cafile
        self._app = None

    def run(self):
        ssl_context = None
        if self._ssl_cafile is not None:
            ssl_context = ssl.create_default_context(cafile=self._ssl_cafile)

        self._app = web.Application()
        self._register_handlers()
        web.run_app(app=self._app, host=self._host, port=self._port, ssl_context=ssl_context)

    def _register_handlers(self):
        home_handler = getattr(self._handler, 'handle_home', None)
        if home_handler is None:
            raise NotImplementedError('Given request handler is not implemented handle_home() method')
        self._app.router.add_get('/', functools.partial(self._handle_wrapper, home_handler))
        logging.info(f'Registered web resource for GET: /')

        for attr in dir(self._handler):
            if attr.startswith(self._get_prefix):
                method_name = attr[len(self._get_prefix):]
                method = getattr(self._handler, attr)
                self._app.router.add_get(f'/{method_name}',
                                         functools.partial(self._handle_wrapper, method))
                logging.info(f'Registered web resource for GET: /{method_name}')

            elif attr.startswith(self._post_prefix):
                method_name = attr[len(self._post_prefix):]
                method = getattr(self._handler, attr)
                self._app.router.add_get(f'/{method_name}',
                                         functools.partial(self._handle_wrapper, method))
                logging.info(f'Registered web resource for POST: /{method_name}')

    def _handle_wrapper(self, handler, request: web.Request):
        args = dict(zip(request.query.keys(), request.query.values()))
        text = handler(args)
        if not isinstance(text, str):
            raise TypeError(f'request handler returned invalid object {type(text)}, string expected')

        return web.Response(text=text)





