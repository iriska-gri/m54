
from project.magnit.marketplace import Marketplace
from project.fiveka.fiveka_setup import Fiveka
from project.auchan.auchan_tasks import Tasks
from project.auchan.auchan_frov import Auchan_frov
from project.metro.metro_task import Metro_task
import sys


if __name__ == '__main__':

   f = Marketplace()
   a= Auchan_frov()
   five = Fiveka()
   m = Metro_task()

   getattr(m ,sys.argv[1])()
