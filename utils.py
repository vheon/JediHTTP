import os
import sys

def AddThirdPartyFolderToSysPath():
  third_party_dir = os.path.join( os.path.dirname( __file__ ), 'third_party' )
  for folder in os.listdir( third_party_dir ):
    sys.path.insert( 0, os.path.realpath( os.path.join( third_party_dir,
                                                        folder ) ) )
