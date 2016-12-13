import sys
import subprocess
sys.path.append('/opt/ops-workload-framework/heat_workload/tools')
from random_gen import getrandom
import os
import string
import time
class create_user():
    def __init__(self,domain,project):
       self.domain=domain
       self.project=project
    def run(self):
       random=getrandom(5)
       self.name="user-"+random.getSuffix()
       comm = "openstack user create --domain "+self.domain+" --project "+self.project+" --enable "+self.name
       subprocess.check_output(comm,shell=True)
       print "Created User... "+self.name
       return self.name
