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

import sys
import hmac
import hashlib
import tempfile
from base64 import b64encode, b64decode

try:
  from configparser import RawConfigParser
except ImportError:
  from ConfigParser import RawConfigParser


if sys.version_info[0] == 3:
  basestring = str
  unicode = str


def encode_string( value ):
  return value.encode('utf-8') if isinstance(value, unicode) else value


def decode_string(value):
  return value if isinstance(value, basestring) else value.decode('utf-8')


def TemporaryHmacSecretFile( secret ):
  """Helper function for passing the hmac secret when starting a JediHTTP server

    with TemporaryHmacSecretFile( 'mysecret' ) as hamc_file:
      jedihttp = subprocess.Popen( .... )

    The JediHTTP Server as soon as it reads the hmac secret will remove the file
  """
  hmac_file = tempfile.NamedTemporaryFile( 'w', delete = False )
  config = RawConfigParser()
  config.add_section( 'HMAC' )
  config.set( 'HMAC', 'secret', secret )
  config.write( hmac_file )
  hmac_file.flush()
  return hmac_file


_HMAC_HEADER = 'x-jedihttp-hmac'


class JediHTTPHmacHelper( object ):
  """Helper class to correctly signing requests and validating responses when
  communicating with a JediHTTP server."""
  def __init__( self, secret ):
    self._secret = encode_string( secret )


  def _HasHeader( self, headers ):
    return _HMAC_HEADER in headers


  def _SetHmacHeader( self, headers, hmac ):
    headers[ _HMAC_HEADER ] = decode_string( b64encode( hmac ) )


  def _GetHmacHeader( self, headers ):
    return b64decode( headers[ _HMAC_HEADER ] )


  def _Hmac( self, content ):
    return hmac.new( self._secret,
                     msg = encode_string( content ),
                     digestmod = hashlib.sha256 ).digest()


  def _ComputeRequestHmac( self, method, path, body ):
    return self._Hmac( b''.join( ( self._Hmac( method ),
                                  self._Hmac( path ),
                                  self._Hmac( body ) ) ) )


  def SignRequestHeaders( self, headers, method, path, body ):
    self._SetHmacHeader( headers, self._ComputeRequestHmac( method, path, body ) )


  def IsRequestAuthenticated( self, headers, method, path, body ):
    if not self._HasHeader( headers ):
      return False

    return compare_digest( self._GetHmacHeader( headers ),
                           self._ComputeRequestHmac( method, path, body ) )


  def SignResponseHeaders( self, headers, body ):
    self._SetHmacHeader( headers, self._Hmac( body ) )


  def IsResponseAuthenticated( self, headers, content ):
    if not self._HasHeader( headers ):
      return False

    return compare_digest( self._GetHmacHeader( headers ),
                           self._Hmac( content ) )



# hmac.compare_digest were introduced in python 2.7.7
if sys.version_info >= ( 2, 7, 7 ):
  from hmac import compare_digest as SecureStringsEqual
else:
  # This is the compare_digest function from python 3.4, adapted for 2.6:
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


def compare_digest( a, b ):
  return SecureStringsEqual( a, b )

