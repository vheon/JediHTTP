import utils
utils.AddThirdPartyFolderToSysPath()

import argparse
import waitress
import handlers

def ParseArgs():
  parser = argparse.ArgumentParser()
  parser.add_argument( '--host', type = str, default = '127.0.0.1',
                       help = 'server hostname')
  parser.add_argument( '--port', type = int, default = 0,
                       help = 'server port')

  return parser.parse_args()


def Main():
  args = ParseArgs()
  waitress.serve( handlers.app,
                  host = args.host,
                  port = args.port )

if __name__ == "__main__":
  Main()
