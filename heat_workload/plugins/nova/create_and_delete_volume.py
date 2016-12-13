import sys
import subprocess
from create import nova_create
from delete import nova_delete
sys.path.append('/opt/ops-workload-framework/heat_workload/plugins/cinder')
from create_volume import create_volume
from delete_volume import delete_volume
import os
import string
import time
class create_and_delete_volume():
    def __init__(self,image,flavor,network,size):
       self.image=image
       self.flavor=flavor
       self.network=network
       self.size=size
    def run(self):
       created=nova_create(self.image,self.flavor,self.network)
       server_name=created.run()
       time.sleep(35)
       volume=create_volume(self.size)
       volume_name=volume.run()
       time.sleep(20)
       comm = "openstack server add volume "+server_name+" "+volume_name
       os.system(comm)
       time.sleep(10)
       print "Volume: "+volume_name+" attached to server "+server_name
       deleted=nova_delete(server_name)
       deleted.run()
       del_volume=delete_volume(volume_name)
       del_volume.run()
