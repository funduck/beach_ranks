from web_server import WebServer, RestRequestHandler
from optparse import OptionParser
import logging

logging.getLogger('RestRequestHandler').setLevel(logging.DEBUG)
logging.getLogger('DB').setLevel(logging.DEBUG)
logging.getLogger('DBSearch').setLevel(logging.DEBUG)
logging.getLogger('DBManage').setLevel(logging.DEBUG)


parser = OptionParser()
parser.add_option('-H', '--host', dest='host', help='host for web-server (0.0.0.0 by default)')
parser.add_option('-P', '--port', dest='port', help='port for web-server (9999 by default)')
(options, args) = parser.parse_args()
host = options.host
port = int(options.port) if options.port is not None else 9999

server = WebServer(RestRequestHandler(), host=options.host, port=port)
server.run()
