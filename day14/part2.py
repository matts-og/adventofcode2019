import sys
import nanofactory

#import logging
#logging.getLogger("nanofactory").setLevel(logging.DEBUG)

filename = sys.argv[1]


print(nanofactory.NanoFactory(filename).output_capacity(
    1000000000000,
    'FUEL'
    ))



