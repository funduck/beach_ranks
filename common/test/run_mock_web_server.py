from common import WebServer

from common.test.mock_request_handler import MockRequestHandler


def test_run_web_server():
    host, port = 'localhost', 9999
    server = WebServer(MockRequestHandler(), host=host, port=port)
    server.run()


if __name__ == '__main__':
    test_run_web_server()
