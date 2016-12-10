import os
import sys
sys.path.append('/opt/ops-workload-framework/heat_workload/tools')
from random_gen import getrandom
import subprocess
class create_volume():
    def __init__(self,size):
       self.size=size
    def create(self):
       random=getrandom(5)
       self.name = "volume-"+random.getSuffix()
       comm = "openstack volume create "+self.name+" --size "+str(self.size)
       os.system(comm)
       print "Created Volume... "+self.name
       return self.name
