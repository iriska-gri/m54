
from project.auchan.auchan_frov import Auchan_frov
from project.auchan.auchan_zn import Auchan_zn
import sys


if __name__ == '__main__':

   f = Auchan_zn()

   getattr(f ,sys.argv[1])()
