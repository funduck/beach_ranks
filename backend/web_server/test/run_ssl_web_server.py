from web_server import WebServer

from web_server.test.mock_request_handler import MockRequestHandler


def test_run_web_server():
    host, port = 'localhost', 9999
    server = WebServer(MockRequestHandler(), host=host, port=port, ssl_files=('cert.pem', 'pkey.pem'))
    server.run()
