

from project.auchan.auchan_tasks import Tasks
import sys


if __name__ == '__main__':

   f = Tasks()

   getattr(f ,sys.argv[1])()
