import subprocess
import os
import sys
sys.path.append('/opt/ops-workload-framework/heat_workload/tools')
from random_gen import getrandom
class create_image():
     def __init__(self,url,disk,container):
         self.url=url
         self.disk=disk
         self.container=container
     def run(self):
         obj=getrandom(5)
         self.name="image-"+obj.getSuffix()
         comm = "openstack --os-image-api 1 image create "+self.name+" --location "+ self.url +" --disk-format "+self.disk+ " --container-format "+self.container
         os.system(comm)
         print self.name+" image created..."
         return self.name 
