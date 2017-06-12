from web_server import WebServer, RestRequestHandler
from optparse import OptionParser
import logging

logging.getLogger('RestRequestHandler').setLevel(logging.DEBUG)

parser = OptionParser()
parser.add_option('-H', '--host', dest='host', help='host for web-server (0.0.0.0 by default)')
parser.add_option('-P', '--port', dest='port', help='port for web-server (80 by default)')
(options, args) = parser.parse_args()
host = options.host
port = int(options.port) if options.port is not None else None

server = WebServer(RestRequestHandler(), host=options.host, port=port)
server.run()
