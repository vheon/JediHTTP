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

import bottle
from bottle import response, request, error
import json
import jedi
import logging


app = bottle.Bottle( __name__ )
logger = logging.getLogger( __name__ )


@app.post( '/healthy' )
def healthy():
  return { 'healthy': True }


@app.post( '/ready' )
def ready():
  return { 'ready': True }


@app.post( '/completions' )
def completions():
  try:
    logger.info( 'received /completions request' )
    script = _GetJediScript( request.json )
    return {
             'completions': [ {
               'name':        completion.name,
               'description': completion.description,
               'docstring':   completion.docstring(),
               'module_path': completion.module_path,
               'line':        completion.line,
               'column':      completion.column
             } for completion in script.completions() ]
           }
  except Exception as e:
    message = str( e )
    logger.info( 'Exception in /completions: {0}'.format( message ) )
    return bottle.HTTPError( 500, message, e )


@app.post( '/gotodefinition' )
def gotodefinition():
  try:
    logger.info( 'received /gotodefinition request' )
    script = _GetJediScript( request.json )
    return {
             'definitions': [ {
               'module_path': definition.module_path,
               'line': definition.line,
               'column': definition.column,
               'in_builtin_module': definition.in_builtin_module(),
               'is_keyword': definition.is_keyword,
               'description': definition.description,
               'docstring': definition.docstring()
             } for definition in script.goto_definitions() ]
           }
  except Exception as e:
    message = str( e )
    logger.info( 'Exception in /gotodefinition: {0}'.format( message ) )
    return bottle.HTTPError( 500, message, e )


@app.post( '/gotoassignment' )
def gotoassignments():
  try:
    logger.info( 'received /gotoassignment request' )
    script = _GetJediScript( request.json )
    return {
             'definitions': [ {
               'module_path': definition.module_path,
               'line': definition.line,
               'column': definition.column,
               'in_builtin_module': definition.in_builtin_module(),
               'is_keyword': definition.is_keyword,
               'description': definition.description,
               'docstring': definition.docstring()
             } for definition in script.goto_assignments() ]
           }
  except Exception as e:
    message = str( e )
    logger.info( 'Exception in /gotoassignment: {0}'.format( message ) )
    return bottle.HTTPError( 500, message, e )


@app.error()
def error( err ):
  return err.body


def _GetJediScript( request_data ):
  try:
    source = request_data[ 'source' ]
    line   = request_data[ 'line' ]
    col    = request_data[ 'col' ]
    path   = request_data[ 'path' ]

    return jedi.Script( source, line, col, path )
  except:
    raise
