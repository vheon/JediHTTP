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


import logging
import httplib
import hmac
import hashlib
from urlparse import urlparse
from bottle import request, response, abort
from base64 import b64decode, b64encode


_HMAC_HEADER = 'x-jedihttp-hmac'


Hmac = None
def HmacGenerator( secret ):
  return lambda content: hmac.new( str( secret ),
                                   msg = content,
                                   digestmod = hashlib.sha256 ).digest()




class HmacPlugin( object ):
  """
  Bottle plugin for hmac request authentication
  http://bottlepy.org/docs/dev/plugindev.html
  """
  name = 'hmac'
  api = 2


  def __init__( self, hmac_secret ):
    global Hmac
    Hmac = HmacGenerator( hmac_secret )
    self._logger = logging.getLogger( __name__ )


  def __call__( self, callback ):
    def wrapper( *args, **kwargs ):
      if not IsLocalRequest():
        self._logger.info( 'Dropping request with bad Host header.' )
        abort( httplib.UNAUTHORIZED, 'Unauthorized, received request from non-local Host.' )
        return

      if not self.IsRequestAuthenticated():
        self._logger.info( 'Dropping request with bad HMAC.' )
        abort( httplib.UNAUTHORIZED, 'Unauthorized, received bad HMAC.' )
        return
      body = callback( *args, **kwargs )
      SetHmacHeader( body )
      return body
    return wrapper


  def IsRequestAuthenticated( self ):
    if _HMAC_HEADER not in request.headers:
      return False

    return SecureStringsEqual( b64decode( request.headers[ _HMAC_HEADER ] ),
                               CalculateRequestHmac( request.method,
                                                     request.path,
                                                     request.body.read() ) )




def CalculateRequestHmac( self, method, path, body, secret ):
  return Hmac( ''.join( ( Hmac( method ), Hmac( path ), Hmac( body ) ) ) )


def IsLocalRequest():
  host = urlparse( 'http://' + request.headers[ 'host' ] ).hostname
  return host == '127.0.0.1' or host == 'localhost'


def SetHmacHeader( self, body ):
  response.headers[ _HMAC_HEADER ] = b64encode( Hmac( body ) )


# This is the compare_digest function from python 3.4, adapted for 2.7:
# http://hg.python.org/cpython/file/460407f35aa9/Lib/hmac.py#l16
#
# Stolen from https://github.com/Valloric/ycmd
def SecureStringsEqual( a, b ):
  """Returns the equivalent of 'a == b', but avoids content based short
  circuiting to reduce the vulnerability to timing attacks."""
  # Consistent timing matters more here than data type flexibility
  if not ( isinstance( a, str ) and isinstance( b, str ) ):
    raise TypeError( "inputs must be str instances" )

  # We assume the length of the expected digest is public knowledge,
  # thus this early return isn't leaking anything an attacker wouldn't
  # already know
  if len( a ) != len( b ):
    return False

  # We assume that integers in the bytes range are all cached,
  # thus timing shouldn't vary much due to integer object creation
  result = 0
  for x, y in zip( a, b ):
    result |= ord( x ) ^ ord( y )
  return result == 0
