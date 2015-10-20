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

import hmac
import hashlib
from base64 import b64encode, b64decode


_HMAC_HEADER = 'x-jedihttp-hmac'


class JediHTTPHmacHelper( object):
  """Helper class to correctly signing requests and validating responses when
  communicating with a JediHTTP server."""
  def __init__( self, secret ):
    self._secret = secret


  def HasHeader( self, headers ):
    return _HMAC_HEADER in headers


  def SetHmacHeader( self, headers, hmac ):
    headers[ _HMAC_HEADER ] = b64encode( hmac )


  def GetHmacHeader( self, headers ):
    return b64decode( headers[ _HMAC_HEADER ] )


  def Hmac( self, content ):
    return hmac.new( str( self._secret ),
                     msg = str( content ),
                     digestmod = hashlib.sha256 ).digest()


  def ComputeRequestHmac( self, method, path, body ):
    return self.Hmac( ''.join( ( self.Hmac( method ),
                                 self.Hmac( path ),
                                 self.Hmac( body ) ) ) )




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
