from web_server import RequestHandler, WebServer


def test_run_web_server():
    host, port = 'localhost', 9999
    server = WebServer(RequestHandler(), host=host, port=port, ssl_files=('cert.pem', 'pkey.pem'))
    server.run()