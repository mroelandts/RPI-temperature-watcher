#!/usr/bin/env python

from flup.server.fcgi import WSGIServer

from temp_app import app

if __name__ == '__main__':
    WSGIServer(app).run()
