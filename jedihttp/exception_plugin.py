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

from bottle import HTTPError

class ExceptionPlugin( object ):
  name = 'exception'
  api = 2

  def __init__( self, logger ):
    self._logger = logger

  def apply( self, handler, route ):
    def wrapper( *args,**kwargs ):
      try:
        return handler( *args, **kwargs )
      except Exception as e:
        message = str( e )
        self._logger.debug( 'Exception in {0}: {1}'.format( route.rule, message ) )
        return HTTPError( 500, message, e )
    return wrapper
