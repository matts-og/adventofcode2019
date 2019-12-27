import sys
import nanofactory

import logging
logging.getLogger("nanofactory").setLevel(logging.DEBUG)

filename = sys.argv[1]

print(nanofactory.NanoFactory(filename).produce(1, 'FUEL'))

