import functools
import ssl
import logging

from aiohttp import web

OK_STATUS = 'OK'


class WebServer:
    def __init__(self, handler, host=None, port=None, ssl_files=None):
        self._handler = handler
        self._host = host
        self._port = port
        self._get_prefix = 'handle_'
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
                self._app.router.add_post(f'/{method_name}',
                                         functools.partial(self._handle_wrapper, method))
                logging.info(f'Registered web resource for POST: /{method_name}')

    async def _handle_wrapper(self, handler, request: web.Request):
        args = dict(zip(request.query.keys(), request.query.values()))
        text = await handler(args)
        if not isinstance(text, str):
            raise TypeError(f'request handler returned invalid object {type(text)}, string expected')

        return web.Response(text=text)





