import os
import create_net import create_net
import sys
sys.path.append('/opt/ops-workload-framework/heat_workload/tools')
from random_gen import getrandom
class create_subnet():
      def __init__(self,net_name):
          self.net_name = net_name
      def run(self):
          obj = getrandom(5)
          self.name = 'subnet-'+obj.getSuffix()
          comm = "openstack subnet create "+self.name+" --network "+self.net_name + " 10.0.0.0/24"
          os.system(comm)
          print "Created subnet "+self.name+" for network: "+self.net_name
          return self.name 
