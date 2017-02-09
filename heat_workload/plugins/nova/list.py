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
class list():
    def __init__(self,count):
       self.count = count
    def run(self):
       poll_obj = poll()
       calculate_obj = Calculate()
       for i in range(0,self.count):
               stopwatch = Stopwatch()
               comm = "openstack server list"
               stopwatch.start()
               os.system(comm)
               TIME_LIST.append(stopwatch.time_elapsed)
               stopwatch.stop()
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
       dict_return['name']="nova.list"
       disp_list.append(dict_return)
       return disp_list

