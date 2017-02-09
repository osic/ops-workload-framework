import os
import sys
sys.path.append('/opt/ops-workload-framework/heat_workload/tools')
from stopwatch import Stopwatch
sys.path.append('/opt/ops-workload-framework/heat_workload/tools')
from calculate import Calculate
from poll import poll
dict_return={}
SERVER_LIST=[]
TIME_LIST=[]
disp_list = []
class delete():
    def __init__(self,names,count):
       self.names=names
       self.count=count
    def run(self):
       poll_obj = poll()
       calculate_obj = Calculate()
       if len(self.names)>0:
          for server in self.names:
                  stopwatch = Stopwatch()  
                  comm = "openstack server delete "+server
                  stopwatch.start()
                  os.system(comm)
                  SERVER_LIST.append(server)
                  while True:
                       delete_status = poll_obj.delete_server(server)
                       if delete_status == 1:
                             TIME_LIST.append(stopwatch.time_elapsed)
                             stopwatch.stop()
                             break
                       elif delete_status == 0:
                             pass
                       elif delete_status == -1:
                            print "Deletion Failed"
                            break
                  print "Deleted server..." +server
          min = calculate_obj.getMin(TIME_LIST)
          max = calculate_obj.getMax(TIME_LIST)
          avg = calculate_obj.getAverage(TIME_LIST)
          print "Min: "+str(min)
          print "Max: "+str(max)
          print "Average: "+str(avg)
          dict_return['server']=SERVER_LIST
          dict_return['min']=min
          dict_return['max']=max
          dict_return['avg']=avg
          dict_return['name']="nova.delete"
          disp_list.append(dict_return)
          return disp_list
