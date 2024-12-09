
from auchan_frov import Frov

import sys


if __name__ == '__main__':

   f = Frov()

   getattr(f ,sys.argv[1])()
