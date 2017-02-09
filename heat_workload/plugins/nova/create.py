import sys
import subprocess
sys.path.append('/opt/ops-workload-framework/heat_workload/tools')
from random_gen import getrandom
sys.path.append('/opt/ops-workload-framework/heat_workload/tools')
from stopwatch import Stopwatch
sys.path.append('/opt/ops-workload-framework/heat_workload/tools')
from calculate import Calculate
from poll import poll
import os
import string
import time
TIME_LIST=[]
dict_return={}
SERVER_LIST=[]
disp_list = []
class create():
    def __init__(self,image,flavor,network,count):
       self.image=image
       self.flavor=flavor
       self.network=network
       self.count=count
    def run(self):
       poll_obj = poll()
       calculate_obj = Calculate()
       for i in range(0,self.count):
            stopwatch = Stopwatch()
            random=getrandom(5)
            self.name="server-"+random.getSuffix()
            comm = "openstack server create "+self.name+" --image "+self.image+" --flavor "+self.flavor+" --nic net-id="+self.network
            subprocess.check_output(comm,shell=True)
            SERVER_LIST.append(self.name)
            stopwatch.start()
            while True:
                  create_status = poll_obj.create_server(self.name)
                  if create_status == 1:
                      TIME_LIST.append(stopwatch.time_elapsed)
                      stopwatch.stop()
                      break
                  elif create_status == 0:
                      pass
                  elif create_status == -1:
                      print "Creation Failed"
                      break
            print "Created Server... "+self.name
       min = calculate_obj.getMin(TIME_LIST)
       max = calculate_obj.getMax(TIME_LIST)
       avg = calculate_obj.getAverage(TIME_LIST)  
       #print_output(min,max,avg,"nova.create",self.count)     
       #print "Min: "+str(min)
       #print "Max: "+str(max)
       #print "Average: "+str(avg)
       dict_return['server']=SERVER_LIST
       dict_return['min']=min
       dict_return['max']=max
       dict_return['avg']=avg
       dict_return['name'] = "nova.create"
       disp_list.append(dict_return)
       return disp_list
