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
from . import utils
import requests
import subprocess
from jedihttp import hmaclib
from os import path
from nose.tools import with_setup
from hamcrest import assert_that, equal_to

try:
  from http import client as httplib
except ImportError:
  import httplib


class HMACAuth( requests.auth.AuthBase ):
  def __init__( self, secret ):
    self._hmachelper = hmaclib.JediHTTPHmacHelper( secret )

  def __call__( self, req ):
    self._hmachelper.SignRequestHeaders( req.headers,
                                         req.method,
                                         req.path_url,
                                         req.body )
    return req


PATH_TO_JEDIHTTP = path.abspath( path.join( path.dirname( __file__ ),
                                            '..', 'jedihttp' ) )

JEDIHTTP = None


def teardown():
  utils.TerminateProcess( JEDIHTTP.pid )


@with_setup( teardown = teardown )
def test_client_request_without_parameters():
  port = 50000
  secret = "secret"

  with hmaclib.TemporaryHmacSecretFile( secret ) as hmac_file:
    command = [ sys.executable,
                '-u', # this flag makes stdout non buffered
                PATH_TO_JEDIHTTP,
                '--port', str( port ),
                '--hmac-file-secret', hmac_file.name ]
    global JEDIHTTP
    JEDIHTTP = utils.SafePopen( command,
                                stderr = subprocess.STDOUT,
                                stdout = subprocess.PIPE )

  # wait for the process to print something, so we know it is ready
  line = JEDIHTTP.stdout.readline().decode( 'utf8' )
  # check if the jedihttp started as expected
  good_start = line.startswith( 'serving on' )
  reason = JEDIHTTP.stdout.read().decode( 'utf8' ) if not good_start else ''
  assert_that( good_start, reason )


  response = requests.post( 'http://127.0.0.1:{0}/ready'.format( port ),
                            auth = HMACAuth( secret ) )

  assert_that( response.status_code, equal_to( httplib.OK ) )

  hmachelper = hmaclib.JediHTTPHmacHelper( secret )
  assert_that( hmachelper.IsResponseAuthenticated( response.headers,
                                                   response.content ) )


@with_setup( teardown = teardown )
def test_client_request_with_parameters():
  port = 50000
  secret = "secret"

  with hmaclib.TemporaryHmacSecretFile( secret ) as hmac_file:
    command = [ sys.executable,
                '-u', # this flag makes stdout non buffered
                PATH_TO_JEDIHTTP,
                '--port', str( port ),
                '--hmac-file-secret', hmac_file.name ]
    global JEDIHTTP
    JEDIHTTP = utils.SafePopen( command,
                                stderr = subprocess.STDOUT,
                                stdout = subprocess.PIPE )

  # wait for the process to print something, so we know it is ready
  line = JEDIHTTP.stdout.readline().decode( 'utf8' )
  # check if the jedihttp started as expected
  good_start = line.startswith( 'serving on' )
  reason = JEDIHTTP.stdout.read().decode( 'utf8' ) if not good_start else ''
  assert_that( good_start, reason )

  filepath = utils.fixture_filepath( 'goto.py' )
  request_data = {
      'source': open( filepath ).read(),
      'line': 10,
      'col': 3,
      'path': filepath
  }

  response = requests.post( 'http://127.0.0.1:{0}/gotodefinition'.format( port ),
                            json = request_data,
                            auth = HMACAuth( secret ) )

  assert_that( response.status_code, equal_to( httplib.OK ) )

  hmachelper = hmaclib.JediHTTPHmacHelper( secret )
  assert_that( hmachelper.IsResponseAuthenticated( response.headers,
                                                   response.content ) )
