import sys
import subprocess
import os
import string
import time
class poll():
    def __init__(self):
        pass
    def create_server(self,server):
       print server
       comm_create = "openstack server show "+server +" -f shell| grep \"os_ext_sts_vm_state\" | cut -d \"=\" -f 2"
       result = subprocess.check_output(comm_create,shell=True)
       print result
       if "\"active\"" in result:
           return 1
       elif "\"building\"" in result:
           return 0
       else:
           return -1
    def delete_server(self,server):
        comm_delete = "openstack server show "+server
        try:
           result = subprocess.check_output(comm_delete,shell=True)
           return 0
        except:
           return 1 
