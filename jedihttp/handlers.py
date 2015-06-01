import bottle
from bottle import response, request
import json
import jedi
import logging


app = bottle.Bottle( __name__ )
logger = logging.getLogger( __name__ )


@app.post( '/healthy' )
def healthy():
  return _Json({'healthy': True})


@app.post( '/ready' )
def ready():
  return _Json({'ready': True})


@app.post( '/completions' )
def completion():
  logger.info( 'received /completions request' )
  script = _GetJediScript( request.json )
  return _Json(
      {
        'completions': [ {
          'name':        completion.name,
          'description': completion.description,
          'docstring':   completion.docstring(),
          'module_path': completion.module_path,
          'line':        completion.line,
          'column':      completion.column
        } for completion in script.completions() ]
      } )


def _GetJediScript( request_data ):
  source = request_data[ 'source' ]
  line   = request_data[ 'line' ]
  col    = request_data[ 'col' ]
  path   = request_data[ 'path' ]

  return jedi.Script( source, line, col, path )


def _Json( data ):
  response.content_type = 'application/json'
  return json.dumps( data )
