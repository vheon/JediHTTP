import bottle
from bottle import response, request
import json
import jedi
import logging


app = bottle.Bottle( __name__ )
logger = logging.getLogger( __name__ )


@app.get( '/healthy' )
def healthy():
  return _Json({})


@app.get( '/ready' )
def ready():
  return _Json({})


@app.post( '/completions' )
def completion():
  logger.info( 'received /completions request' )
  script = _GetJediScript( request.json )
  return _Json(
      {
        'completions': [ {
          'name':        completion.name,
          'description': completion.description,
          'docstring':   completion.docstring()
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
