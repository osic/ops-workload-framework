import os
import sys
sys.path.append('/opt/ops-workload-framework/heat_workload/tools')
from random_gen import getrandom
class create_net():
      def run(self):
         obj = getrandom(5)
         self.name = 'network-'+obj.getSuffix()
         comm = "openstack network create "+ self.name
         os.system(comm)
         print "Created network: "+self.name
         return self.name
