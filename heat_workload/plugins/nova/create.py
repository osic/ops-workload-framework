import sys
import subprocess
sys.path.append('/opt/ops-workload-framework/heat_workload/tools')
from random_gen import getrandom
import os
import string
import time
class nova_create():
    def __init__(self,image,flavor,network):
       self.image=image
       self.flavor=flavor
       self.network=network
    def run(self):
       random=getrandom(5)
       self.name="server-"+random.getSuffix()
       comm = "openstack server create "+self.name+" --image "+self.image+" --flavor "+self.flavor+" --nic net-id="+self.network
       subprocess.check_output(comm,shell=True)
       print "Created Server... "+self.name
       return self.name
