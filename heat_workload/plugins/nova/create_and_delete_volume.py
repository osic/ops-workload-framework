import sys
import subprocess
from create import create
from delete import delete
sys.path.append('/opt/ops-workload-framework/heat_workload/plugins/cinder')
from create_volume import create_volume
from delete_volume import delete_volume
import os
import string
import time
class create_and_delete_volume():
    def __init__(self,image,flavor,network,size,count):
       self.image=image
       self.flavor=flavor
       self.network=network
       self.size=size
       self.count=count
    def run(self):
       created=create(self.image,self.flavor,self.network,self.count)
       server_name=created.run()
       time.sleep(10)
       volume=create_volume(self.size)
       volume_name=volume.run()
       time.sleep(10)
       comm = "openstack server add volume "+server_name+" "+volume_name
       os.system(comm)
       time.sleep(10)
       print "Volume: "+volume_name+" attached to server "+server_name
       deleted=delete(server_name)
       deleted.run()
       del_volume=delete_volume(volume_name)
       del_volume.run()
