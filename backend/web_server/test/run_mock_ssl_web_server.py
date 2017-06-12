import os

from web_server import WebServer

from web_server.test.mock_request_handler import MockRequestHandler


def test_run_web_server():
    host, port = 'localhost', 9999
    path = os.path.dirname(os.path.abspath(__file__))
    server = WebServer(MockRequestHandler(), host=host, port=port, ssl_files=(f'{path}/cert.pem', f'{path}/pkey.pem'))
    server.run()


if __name__ == '__main__':
    test_run_web_server()
