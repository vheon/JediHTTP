#     Copyright 2015 Cedraro Andrea <a.cedraro@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
#    limitations under the License.


from jedihttp import utils
utils.AddVendorFolderToSysPath()

import jedi
import logging
import json
import bottle
from jedihttp import hmaclib
from bottle import response, request, Bottle
from threading import Lock

try:
  import httplib
except ImportError:
  from http import client as httplib


# num bytes for the request body buffer; request.json only works if the request
# size is less than this
bottle.Request.MEMFILE_MAX = 1000 * 1024

logger = logging.getLogger( __name__ )
app = Bottle( __name__ )

# Jedi is not thread safe.
jedi_lock = Lock()


@app.post( '/healthy' )
def healthy():
  logger.debug( 'received /healthy request' )
  return _JsonResponse( True )


@app.post( '/ready' )
def ready():
  logger.debug( 'received /ready request' )
  return _JsonResponse( True )


@app.post( '/completions' )
def completions():
  logger.debug( 'received /completions request' )
  with jedi_lock:
    script = _GetJediScript( request.json )
    response = _FormatCompletions( script.completions() )
  return _JsonResponse( response )


@app.post( '/gotodefinition' )
def gotodefinition():
  logger.debug( 'received /gotodefinition request' )
  with jedi_lock:
    script = _GetJediScript( request.json )
    response = _FormatDefinitions( script.goto_definitions() )
  return _JsonResponse( response )


@app.post( '/gotoassignment' )
def gotoassignments():
  logger.debug( 'received /gotoassignment request' )
  with jedi_lock:
    request_json = request.json
    follow_imports = ( 'follow_imports' in request_json and
                       request_json[ 'follow_imports' ] )
    script = _GetJediScript( request_json )
    response = _FormatDefinitions( script.goto_assignments( follow_imports ) )
  return _JsonResponse( response )


@app.post( '/usages' )
def usages():
  logger.debug( 'received /usages request' )
  with jedi_lock:
    script = _GetJediScript( request.json )
    response = _FormatDefinitions( script.usages() )
  return _JsonResponse( response )


@app.post( '/names' )
def names():
  logger.debug( 'received /names request' )
  with jedi_lock:
    definitions = _GetJediNames( request.json )
    response = _FormatDefinitions( definitions )
  return _JsonResponse( response )


@app.post( '/preload_module' )
def preload_module():
  logger.debug( 'received /preload_module request' )
  with jedi_lock:
    jedi.preload_module( *request.json[ 'modules' ] )
  return _JsonResponse( True )


def _FormatCompletions( completions ):
  return {
      'completions': [ {
          'module_path': completion.module_path,
          'name':        completion.name,
          'type':        completion.type,
          'line':        completion.line,
          'column':      completion.column,
          'docstring':   completion.docstring(),
          'description': completion.description,
      } for completion in completions ]
  }


def _FormatDefinitions( definitions ):
  return {
      'definitions': [ {
          'module_path':       definition.module_path,
          'name':              definition.name,
          'type':              definition.type,
          'in_builtin_module': definition.in_builtin_module(),
          'line':              definition.line,
          'column':            definition.column,
          'docstring':         definition.docstring(),
          'description':       definition.description,
          'full_name':         definition.full_name,
          'is_keyword':        definition.is_keyword
      } for definition in definitions ]
  }


def _GetJediScript( request_data ):
  return jedi.Script( request_data[ 'source' ],
                      request_data[ 'line' ],
                      request_data[ 'col' ],
                      request_data[ 'source_path' ] )


def _GetJediNames( request_data ):
  return jedi.names( source = request_data[ 'source' ],
                     path = request_data[ 'path' ],
                     all_scopes = request_data.get( 'all_scopes', False ),
                     definitions = request_data.get( 'definitions', True ),
                     references = request_data.get( 'references', False ) )


@app.error( httplib.INTERNAL_SERVER_ERROR )
def ErrorHandler( httperror ):
  body = _JsonResponse( {
    'exception': httperror.exception,
    'message': str( httperror.exception ),
    'traceback': httperror.traceback
  } )
  if 'jedihttp.hmac_secret' in app.config:
    hmac_secret = app.config[ 'jedihttp.hmac_secret' ]
    hmachelper = hmaclib.JediHTTPHmacHelper( hmac_secret )
    hmachelper.SignResponseHeaders( response.headers, body )
  return body


def _JsonResponse( data ):
  response.content_type = 'application/json'
  return json.dumps( data, default = _Serializer )


def _Serializer( obj ):
  try:
    serialized = obj.__dict__.copy()
    serialized[ 'TYPE' ] = type( obj ).__name__
    return serialized
  except AttributeError:
    return str( obj )
