import os
class delete_net():
     def __init__(self,name):
         self.name = name
     def run(self):
         comm = "openstack subnet delete "+self.name
         os.system(comm)
         print "Deleted network: "+self.name
        
