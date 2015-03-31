import os
from webtest import TestApp
from .. import handlers
from nose.tools import ok_
from hamcrest import ( assert_that, only_contains, all_of, has_key, has_items,
                       has_entry )

def CompletionEntry( name ):
    return has_entry( 'name', name )


def valid_completions():
    return all_of( has_key( 'docstring' ),
                   has_key( 'name' ),
                   has_key( 'description' ) )


def test_healthy():
    app = TestApp( handlers.app )
    ok_( app.get( '/healthy' ) )


def test_ready():
    app = TestApp( handlers.app )
    ok_( app.get( '/ready' ) )


def test_completion():
    app = TestApp( handlers.app )
    dir_of_current_script = os.path.dirname( os.path.abspath( __file__ ) )
    filepath = os.path.join( dir_of_current_script, 'fixtures', 'basic.py' )
    request_data = {
            'filepath': filepath,
            'line_num': 7,
            'column_num': 2,
            'contents': open( filepath ).read()
    }

    completions = app.post_json( '/completions',
                                 request_data ).json[ 'completions' ]

    assert_that( completions, only_contains( valid_completions() ) )
    assert_that( completions, has_items( CompletionEntry( 'a' ),
                                         CompletionEntry( 'b' ) ) )
