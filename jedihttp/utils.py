import os
import sys


def AddVendorFolderToSysPath():
  vendor_folder = os.path.join( os.path.dirname( __file__ ),
                                '..',
                                'vendor' )

  for folder in os.listdir( vendor_folder ):
    sys.path.insert( 0, os.path.realpath( os.path.join( vendor_folder,
                                                        folder ) ) )
