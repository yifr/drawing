#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from server import app
import posixpath

class ScriptNameStripper(object):
   def __init__(self, app):
       self.app = app

   def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = ''
        return self.app(environ, start_response)

app = ScriptNameStripper(app)

WSGIServer(app).run()
		
