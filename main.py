
from project.magnit.marketplace import Marketplace
from project.fiveka.fiveka_setup import Fiveka
from project.auchan.auchan_tasks import Tasks
from project.auchan.auchan_frov import Auchan_frov
import sys


if __name__ == '__main__':

   f = Marketplace()
   a= Auchan_frov()
   five = Fiveka()

   getattr(five ,sys.argv[1])()
