import sys
import subprocess
from create import create
from delete import delete
import time
sys.path.append("../../tools/")
from prettyoutput import Prettyoutput
dict_delete={}
disp_list = [0,0]
class create_and_delete():
      def __init__(self,image,flavor,network,count):
         self.image=image
         self.flavor=flavor
         self.network=network
         self.count = count
      def run(self):
         created = create(self.image,self.flavor,self.network,self.count)
         disp_list=created.run()
         print disp_list
         if len(disp_list[0]['server'])>0:
             deleted = delete(disp_list[0]['server'],self.count)
             disp_list.append(deleted.run()[0])
             #x = PrettyTable(["Task Name", "Minimum Time", "Average Time", "Maximum Time"])
             #x.add_row(["nova.create",dict_values['min'], dict_values['avg'], dict_values['max']])
             #x.add_row(["nova.delete",dict_delete['min'], dict_delete['avg'], dict_delete['max']])
             #x.add_row(["TOTAL", TOTAL_MIN, TOTAL_AVG, TOTAL_MAX])
             #print x
             print disp_list
             return disp_list
             #pretty_obj = Prettyoutput(disp_list)
             #pretty_obj.display()
#obj=create_and_delete("ubuntu.medium","custom.workload.medium","net1.large")
#obj.run()
