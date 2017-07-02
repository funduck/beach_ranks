import logging
from optparse import OptionParser

from config.config import Config, initConfig

parser = OptionParser()
parser.add_option('-H', '--host', dest='host', help='host for web-server (0.0.0.0 by default)')
parser.add_option('-P', '--port', dest='port', help='port for web-server (9999 by default)')
parser.add_option('-M', '--mode', dest='mode', help='mode for bot (can be test, by default is None, for unittest use unittest)')
(options, args) = parser.parse_args()
host = options.host

initConfig(options.mode)

from common import WebServer
from rest_service.request_handler import RestRequestHandler

logging.getLogger('RestRequestHandler').setLevel(logging.DEBUG)
logging.getLogger('DB').setLevel(logging.DEBUG)
logging.getLogger('DBSearch').setLevel(logging.DEBUG)
logging.getLogger('DBManage').setLevel(logging.DEBUG)
logging.getLogger('WebServer').setLevel(logging.DEBUG)

host = options.host
port = int(options.port) if options.port is not None else Config.rest_service.port

server = WebServer(RestRequestHandler(), host=host, port=port)
server.run()
