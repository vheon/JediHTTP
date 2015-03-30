import sys
import os

sys.path.insert( 0, os.path.join(
                        os.path.dirname( os.path.abspath( __file__ ) ),
                        '..' ) )

from webtest import TestApp
import handlers
from nose.tools import ok_

def test_healthy():
    app = TestApp( handlers.app )
    ok_( app.get( '/healthy' ) )


def test_ready():
    app = TestApp( handlers.app )
    ok_( app.get( '/ready' ) )
