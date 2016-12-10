import sys
import subprocess
from create import nova_create
from delete import nova_delete
import time
class create_and_delete():
      def __init__(self,image,flavor,network):
         self.image=image
         self.flavor=flavor
         self.network=network
      def run(self):
         created = nova_create(self.image,self.flavor,self.network)
         server_name=created.create_server()
         time.sleep(30)
         deleted = nova_delete(server_name)
         deleted.delete_server()
#obj=create_and_delete("ubuntu.medium","custom.workload.medium","net1.large")
#obj.run()
