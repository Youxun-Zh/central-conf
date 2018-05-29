import argparse

import settings
import strix.app
from urls import urls
from strix.httpserver import HTTPServer


class Application(strix.app.Application):
    def __init__(self):
        handlers = urls
        settings_kwargs = {
            "debug": settings.DEBUG,
            "cookie_secret": settings.SECRET_KEY,
        }
        super(Application, self).__init__(handlers, **settings_kwargs)


def run(host, port):
    app = Application()
    server = HTTPServer(app, host, port)
    server.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run server on the host, port!")
    parser.add_argument('--host', help='The server host.', default="127.0.0.1")
    parser.add_argument('--port', help='The server port.', type=int, default=8080)
    args = parser.parse_args()

    host = args.host
    port = args.port
    run(host, port)