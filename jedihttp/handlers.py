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

import jedi
import logging
from bottle import request, Bottle
from jedihttp.logger_plugin import LoggerPlugin
from jedihttp.exception_plugin import ExceptionPlugin


logger = logging.getLogger( __name__ )
app = Bottle( __name__ )
app.install( LoggerPlugin( logger ) )
app.install( ExceptionPlugin( logger ) )


@app.post( '/healthy' )
def healthy():
  return { 'healthy': True }


@app.post( '/ready' )
def ready():
  return { 'ready': True }


@app.post( '/completions' )
def completions():
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


@app.post( '/gotodefinition' )
def gotodefinition():
  script = _GetJediScript( request.json )
  return _FormatGoToDefinitions( script.goto_definitions() )


@app.post( '/gotoassignment' )
def gotoassignments():
  script = _GetJediScript( request.json )
  return _FormatGoToDefinitions( script.goto_assignments() )


def _FormatGoToDefinitions( definitions ):
  return {
            'definitions': [ {
              'module_path':       definition.module_path,
              'line':              definition.line,
              'column':            definition.column,
              'in_builtin_module': definition.in_builtin_module(),
              'is_keyword':        definition.is_keyword,
              'description':       definition.description,
              'docstring':         definition.docstring()
            } for definition in definitions ]
          }


@app.error()
def error( err ):
  return err.body


def _GetJediScript( request_data ):
  return jedi.Script( request_data[ 'source' ],
                      request_data[ 'line' ],
                      request_data[ 'col' ],
                      request_data[ 'path' ] )
