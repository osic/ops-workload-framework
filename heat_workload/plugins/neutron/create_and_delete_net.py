import sys
import subprocess
from create_net import create_net as net_create
from delete_net import delete_net as net_delete
import time
class create_and_delete_net():
      def run(self):
         created = net_create()
         net_name=created.run()
         time.sleep(10)
         deleted = net_delete(net_name)
         deleted.run()
#obj=create_and_delete("ubuntu.medium","custom.workload.medium","net1.large")
#obj.run()
