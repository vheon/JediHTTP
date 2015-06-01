from jedihttp import utils
utils.AddVendorFolderToSysPath()

import os
import sys
from webtest import TestApp
from jedihttp import handlers
from nose.tools import ok_
from unittest import SkipTest, skipIf
from hamcrest import ( assert_that, only_contains, all_of, is_not, has_key,
                       has_item, has_items, has_entry )

import bottle
bottle.debug( True )


py3only = skipIf( sys.version_info < ( 3, 0 ), "Python 3.x only test" )


def fixture_filepath( filename ):
  dir_of_current_script = os.path.dirname( os.path.abspath( __file__ ) )
  return os.path.join( dir_of_current_script, 'fixtures', filename )


def CompletionEntry( name ):
  return has_entry( 'name', name )


def valid_completions():
  return all_of( has_key( 'docstring' ),
                 has_key( 'name' ),
                 has_key( 'description' ) )


def test_healthy():
  app = TestApp( handlers.app )
  ok_( app.post( '/healthy' ) )


def test_ready():
  app = TestApp( handlers.app )
  ok_( app.post( '/ready' ) )


def test_completion():
  app = TestApp( handlers.app )
  filepath = fixture_filepath( 'basic.py' )
  request_data = {
      'source': open( filepath ).read(),
      'line': 7,
      'col': 2,
      'path': filepath
  }

  completions = app.post_json( '/completions',
                               request_data ).json[ 'completions' ]

  assert_that( completions, only_contains( valid_completions() ) )
  assert_that( completions, has_items( CompletionEntry( 'a' ),
                                       CompletionEntry( 'b' ) ) )


@py3only
def test_py3():
  app = TestApp( handlers.app )
  filepath = fixture_filepath( 'py3.py' )
  request_data = {
      'source': open( filepath ).read(),
      'line': 7,
      'col': 11,
      'path': filepath
  }

  completions = app.post_json( '/completions',
                                request_data ).json[ 'completions' ]

  assert_that( completions, has_item( CompletionEntry( 'values' ) ) )
  assert_that( completions, is_not( has_item( CompletionEntry( 'itervalues' ) ) ) )
