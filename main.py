
from project.magnit.marketplace import Marketplace
from project.auchan.auchan_tasks import Tasks
from project.auchan.auchan_frov import Auchan_frov
import sys


if __name__ == '__main__':

   f = Marketplace()
   a= Auchan_frov()

   getattr(f ,sys.argv[1])()
