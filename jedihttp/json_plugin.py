#     Copyright 2016 Cedraro Andrea <a.cedraro@gmail.com>
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


import logging
from bottle import response
from jedihttp.utils import JsonResponse

class JsonPlugin( object ):
  """
  Bottle plugin for returning json response the way I like it
  http://bottlepy.org/docs/dev/plugindev.html
  """
  name = 'alljson'
  api = 2


  def __call__( self, callback ):
    def wrapper( *args, **kwargs ):
      body = callback( *args, **kwargs )
      return JsonResponse( body )
    return wrapper
