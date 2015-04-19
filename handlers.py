import os
import sys

third_party_dir = os.path.join( os.path.dirname( __file__ ), 'third_party' )
for folder in os.listdir( third_party_dir ):
  sys.path.insert( 0, os.path.realpath( os.path.join( third_party_dir,
                                                      folder ) ) )

import bottle
from bottle import response, request
import json
import jedi


app = bottle.Bottle( __name__ )


@app.get( '/healthy' )
def healthy():
  return _Json({})


@app.get( '/ready' )
def ready():
  return _Json({})


@app.post( '/completions' )
def completion():
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
  filename = request_data[ 'filepath' ]
  contents = request_data[ 'contents' ]
  line     = request_data[ 'line_num' ]
  column   = request_data[ 'column_num' ]

  return jedi.Script( contents, line, column, filename )


def _Json( data ):
  response.content_type = 'application/json'
  return json.dumps( data )
