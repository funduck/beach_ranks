from aiohttp import web
import ssl
from .request_handler import RequestHandler


class WebServer:
    def __init__(self, handler: RequestHandler, ssl_cafile=None):
        self._handler = handler
        self._get_prefix = 'handle_'
        self._post_prefix = 'post_'
        self._ssl_cafile = ssl_cafile
        self._app = None

    def run(self):
        ssl_context = None
        if self._ssl_cafile is not None:
            ssl_context = ssl.create_default_context(cafile=self._ssl_cafile)

        self._app = web.Application()
        self.register_handlers()
        web.run_app(app=self._app, ssl_context=ssl_context)

    def register_handlers(self):
        for attr in dir(self._handler):
            if attr.startswith(self._get_prefix):
                method_name = attr[len(self._post_prefix):]
                method = getattr(self._handler, attr)
                self._app.router.add_get('/' + method_name, method)
            elif attr.startswith(self._post_prefix):
                method_name = attr[len(self._post_prefix):]
                method = getattr(self._handler, attr)
                self._app.router.add_get('/' + method_name, method)


