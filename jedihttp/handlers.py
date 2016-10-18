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

import contextlib
import jedi
import logging
import json
import bottle
from bottle import response, request, Bottle
from jedihttp import hmaclib
from jedihttp.compatibility import iteritems
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

# For efficiency, we store the default values of the global Jedi settings. See
# https://jedi.readthedocs.io/en/latest/docs/settings.html
default_settings = {
    'case_insensitive_completion'     :
        jedi.settings.case_insensitive_completion,
    'add_bracket_after_function'      :
        jedi.settings.add_bracket_after_function,
    'no_completion_duplicates'        : jedi.settings.no_completion_duplicates,
    'cache_directory'                 : jedi.settings.cache_directory,
    'use_filesystem_cache'            : jedi.settings.cache_directory,
    'fast_parser'                     : jedi.settings.fast_parser,
    'dynamic_array_additions'         : jedi.settings.dynamic_array_additions,
    'dynamic_params'                  : jedi.settings.dynamic_params,
    'dynamic_params_for_other_modules':
        jedi.settings.dynamic_params_for_other_modules,
    'additional_dynamic_modules'      :
        jedi.settings.additional_dynamic_modules,
    'auto_import_modules'             : jedi.settings.auto_import_modules
}


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
    request_json = request.json
    with _CustomSettings( request_json ):
      script = _GetJediScript( request_json )
      response = _FormatCompletions( script.completions() )
  return _JsonResponse( response )


@app.post( '/gotodefinition' )
def gotodefinition():
  logger.debug( 'received /gotodefinition request' )
  with jedi_lock:
    request_json = request.json
    with _CustomSettings( request_json ):
      script = _GetJediScript( request_json )
      response = _FormatDefinitions( script.goto_definitions() )
  return _JsonResponse( response )


@app.post( '/gotoassignment' )
def gotoassignments():
  logger.debug( 'received /gotoassignment request' )
  with jedi_lock:
    request_json = request.json
    follow_imports = request_json.get( 'follow_imports', False )
    with _CustomSettings( request_json ):
      script = _GetJediScript( request_json )
      response = _FormatDefinitions( script.goto_assignments( follow_imports ) )
  return _JsonResponse( response )


@app.post( '/usages' )
def usages():
  logger.debug( 'received /usages request' )
  with jedi_lock:
    request_json = request.json
    with _CustomSettings( request_json ):
      script = _GetJediScript( request_json )
      response = _FormatDefinitions( script.usages() )
  return _JsonResponse( response )


@app.post( '/names' )
def names():
  logger.debug( 'received /names request' )
  with jedi_lock:
    request_json = request.json
    with _CustomSettings( request_json ):
      definitions = _GetJediNames( request_json )
      response = _FormatDefinitions( definitions )
  return _JsonResponse( response )


@app.post( '/preload_module' )
def preload_module():
  logger.debug( 'received /preload_module request' )
  with jedi_lock:
    request_json = request.json
    with _CustomSettings( request_json ):
      jedi.preload_module( *request_json[ 'modules' ] )
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


def _SetJediSettings( settings ):
  for name, value in iteritems( settings ):
    setattr( jedi.settings, name, value )


@contextlib.contextmanager
def _CustomSettings( request_data ):
  settings = request_data.get( 'settings' )
  if not settings:
    yield
    return
  try:
    _SetJediSettings( settings )
    yield
  finally:
    _SetJediSettings( default_settings )


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
