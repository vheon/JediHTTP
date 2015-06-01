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
  try:
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
  except Exception as e:
    return _Json(
        {
          'message': str( e )
        }, status = 404 )


@app.post( '/gotodefinition' )
def gotodefinition():
  try:
    logger.info( 'received /gotodefinition request' )
    script = _GetJediScript( request.json )
    return _Json(
        {
          'definitions': [ {
            'module_path': definition.module_path,
            'line': definition.line,
            'column': definition.column,
            'in_builtin_module': definition.in_builtin_module(),
            'is_keyword': definition.is_keyword,
            'description': definition.description
          } for definition in script.goto_definitions() ]
        } )
  except Exception as e:
    return _Json(
        {
          'message': str( e )
        }, status = 404 )


def _GetJediScript( request_data ):
  try:
    source = request_data[ 'source' ]
    line   = request_data[ 'line' ]
    col    = request_data[ 'col' ]
    path   = request_data[ 'path' ]

    return jedi.Script( source, line, col, path )
  except:
    raise


def _Json( data, status = 200 ):
  response.content_type = 'application/json'
  response.status = status
  return json.dumps( data )
