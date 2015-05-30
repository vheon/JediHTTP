import utils
utils.AddVendorFolderToSysPath()

import argparse
import waitress
import handlers

def ParseArgs():
  parser = argparse.ArgumentParser()
  parser.add_argument( '--port', type = int, default = 0,
                       help = 'server port')

  return parser.parse_args()


def Main():
  args = ParseArgs()
  waitress.serve( handlers.app,
                  host = '127.0.0.1',
                  port = args.port )

if __name__ == "__main__":
  Main()
